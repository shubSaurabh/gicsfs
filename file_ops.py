# file_ops.py
import os
import logging
from encryption import AESEncryptor
import base64

class FileManager:
    def __init__(self, base_directory, db_manager, logger=None):
        self.base_directory = base_directory
        self.db_manager = db_manager
        self.logger = logger or logging.getLogger("SecureFileStorage")

    def _get_user_directory(self, username):
        """Get or create a user-specific subdirectory."""
        user_dir = os.path.join(self.base_directory, username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            self.logger.info(f"User directory created at {user_dir}")
        return user_dir

    def upload(self, username, source_path):
        """Encrypt and upload a file."""
        try:
            # Ensure user tables exist
            self.db_manager.initialize_user_tables(username)

            # Get the user's AES key and salt or generate new ones
            self.logger.info(f"Getting user key and salt for {username}")
            user_key, user_salt = self.db_manager.get_user_key_and_salt(username)
            self.logger.debug(f"User key and salt: {user_key}, {user_salt}")
            if user_key is None or user_salt is None:
                # Generate a new AES key and salt for the user
                user_key, user_salt = AESEncryptor.generate_key_and_salt()
                self.logger.debug(f"Generated new user key and salt: {user_key}, {user_salt}")
                self.db_manager.insert_user_key_and_salt(username, user_key, user_salt)
                self.logger.info(f"Inserted new user key and salt for {username}")

            # Use this key and salt for encryption
            salt = base64.b64decode(user_salt) if isinstance(user_salt, str) else user_salt
            encryptor = AESEncryptor(user_key, salt, None, self.logger)

            user_dir = self._get_user_directory(username)
            self.logger.debug(f"User directory: {user_dir}")
            filename = os.path.basename(source_path)
            self.logger.debug(f"Filename: {filename}")
            target_path = os.path.join(user_dir, f"{filename}.enc")
            self.logger.debug(f"Target path: {target_path}")

            with open(source_path, 'rb') as file:
                data = file.read()

            encrypted_data = encryptor.encrypt(data.decode('utf-8'))
            self.logger.debug(f"Encrypted data: {encrypted_data}")
            with open(target_path, 'w') as file:
                file.write(encrypted_data)

            # Insert file metadata into the database
            key_id = self.db_manager.get_user_key_id(username)
            self.db_manager.insert_file_metadata(username, filename, target_path, key_id)

            self.logger.info(f"File '{filename}' uploaded and encrypted successfully.")
            print(f"File '{filename}' uploaded and encrypted successfully.")
        except Exception as e:
            self.logger.error(f"Error during file upload: {e}")
            raise

    def download(self, username, filename):
        """Decrypt and download a file."""
        try:
            # Retrieve file metadata
            file_metadata = self.db_manager.retrieve_file_metadata(username, filename)

            if not file_metadata:
                print(f"File '{filename}' not found or deleted.")
                self.logger.warning(f"File '{filename}' not found or deleted.")
                return

            encrypted_path = file_metadata[2]

            # Retrieve user's AES key and salt from the database
            user_key, user_salt = self.db_manager.get_user_key_and_salt(username)
            if not user_key or not user_salt:
                raise Exception(f"No encryption key or salt found for user '{username}'.")

            encryptor = AESEncryptor(user_key, base64.b64decode(user_salt.encode()), None, self.logger)

            with open(encrypted_path, 'r') as file:
                encrypted_data = file.read()

            decrypted_data = encryptor.decrypt(encrypted_data)
            output_path = os.path.join(os.getcwd(), filename)

            with open(output_path, 'w') as file:
                file.write(decrypted_data)

            self.db_manager.update_download_date(username, filename)
            self.logger.info(f"File '{filename}' decrypted and downloaded successfully.")
            print(f"File '{filename}' decrypted and downloaded successfully to {output_path}.")
        except Exception as e:
            self.logger.error(f"Error during file download: {e}")
            raise

    def delete(self, username, filename):
        """Delete an encrypted file."""
        try:
            # Retrieve file metadata
            file_metadata = self.db_manager.retrieve_file_metadata(username, filename)

            if not file_metadata:
                print(f"File '{filename}' not found.")
                self.logger.warning(f"File '{filename}' not found.")
                return

            encrypted_path = file_metadata[2]

            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
                self.db_manager.mark_file_deleted(username, filename)
                self.logger.info(f"File '{filename}' deleted successfully.")
                print(f"File '{filename}' deleted successfully.")
            else:
                self.logger.warning(f"File '{filename}' not found on disk.")
                print(f"File '{filename}' not found on disk.")
        except Exception as e:
            self.logger.error(f"Error during file deletion: {e}")
            raise

    def list_files(self, username):
        """List all files and their metadata for the user."""
        try:
            files = self.db_manager.list_user_files(username)

            if files:
                print(f"Files for user '{username}':")
                for file in files:
                    print(f"File Name: {file['file_name']}")
                    print(f"  Uploaded At: {file['uploaded_at']}")
                    print(f"  Last Downloaded: {file['download_date'] or 'Never'}")
                    print(f"  Shared With: {file['shared_user'] or 'Not shared'}")
                    print("--------------------")
                self.logger.info(f"Listed files for user '{username}'.")
            else:
                print(f"No files found for user '{username}'.")
                self.logger.info(f"No files found for user '{username}'.")
        except Exception as e:
            self.logger.error(f"Error during listing files: {e}")
            e = 'Error during listing files, please contact the admin.'
            raise

    def share(self, username, filename, shared_users):
        """Share a file with other users."""
        try:
            # Validate that the file exists
            file_metadata = self.db_manager.retrieve_file_metadata(username, filename)
            if not file_metadata:
                print(f"File '{filename}' not found.")
                self.logger.warning(f"File '{filename}' not found.")
                return

            # Validate shared usernames
            valid_users = self.db_manager.list_all_users()
            invalid_users = [user for user in shared_users if user not in valid_users]
            if invalid_users:
                print(f"Invalid usernames: {', '.join(invalid_users)}")
                return

            self.db_manager.share_file(username, filename, shared_users)
            print(f"File '{filename}' shared with: {', '.join(shared_users)}")
            self.logger.info(f"File '{filename}' shared with: {', '.join(shared_users)}")
        except Exception as e:
            self.logger.error(f"Error during file sharing: {e}")
            raise

    def download_shared_file(self, owner_username, filename, requesting_username):
        """Download a shared file."""
        try:
            # Retrieve file metadata
            file_metadata = self.db_manager.get_shared_file_metadata(owner_username, filename, requesting_username)

            if not file_metadata:
                print(f"File '{filename}' not found or not shared with you.")
                self.logger.warning(f"File '{filename}' not found or not shared with user '{requesting_username}'.")
                return

            encrypted_path = file_metadata[2]

            # Retrieve owner's AES key and salt from the database
            user_key, user_salt = self.db_manager.get_user_key_and_salt(owner_username)
            if not user_key or not user_salt:
                raise Exception(f"No encryption key or salt found for user '{owner_username}'.")

            encryptor = AESEncryptor(user_key, base64.b64decode(user_salt.encode()), None, self.logger)

            with open(encrypted_path, 'r') as file:
                encrypted_data = file.read()

            decrypted_data = encryptor.decrypt(encrypted_data)
            output_path = os.path.join(os.getcwd(), filename)

            with open(output_path, 'w') as file:
                file.write(decrypted_data)

            self.logger.info(f"Shared file '{filename}' decrypted and downloaded successfully.")
            print(f"Shared file '{filename}' decrypted and downloaded successfully to {output_path}.")
        except Exception as e:
            self.logger.error(f"Error during shared file download: {e}")
            raise
