# db_manager.py
from pysqlcipher3 import dbapi2 as sqlite
import logging
import base64

class SQLiteManager:
    def __init__(self, db_path, logger=None):
        self.db_path = db_path
        self.logger = logger or logging.getLogger("SecureFileStorage")
        self.conn = None

    def connect(self, master_password):
        """Connect to the SQLCipher database using the master password."""
        try:
            self.conn = sqlite.connect(self.db_path)
            self.conn.execute(f"PRAGMA key = '{master_password}'")
            # Verify the key
            self.conn.execute("SELECT count(*) FROM sqlite_master")
            self.logger.info("Connected to SQLCipher database successfully.")
        except sqlite.DatabaseError as e:
            self.logger.error(f"Failed to connect to SQLCipher database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to database: {e}")
            raise

    def initialize_user_tables(self, username):
        """Create tables for storing user keys and file metadata if they don't exist."""
        try:
            cursor = self.conn.cursor()

            # Create the key management table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {username}_keys (
                    id INTEGER PRIMARY KEY,
                    aes_key TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create the file metadata table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {username}_files (
                    id INTEGER PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    encrypted_path TEXT NOT NULL,
                    key_id INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    download_date TIMESTAMP,
                    delete_date TIMESTAMP,
                    shared_user TEXT,
                    FOREIGN KEY (key_id) REFERENCES {username}_keys(id)
                )
            ''')

            self.conn.commit()
            self.logger.info(f"User tables created for {username}.")
        except Exception as e:
            self.logger.error(f"Error initializing user tables: {e}")
            raise

    def insert_user_key_and_salt(self, username, aes_key, salt):
        """Insert a user's AES key and salt into the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                INSERT INTO {username}_keys (aes_key, salt)
                VALUES (?, ?)
            ''', (aes_key, salt))
            self.conn.commit()
            self.logger.info(f"User AES key and salt inserted for {username}.")
        except Exception as e:
            self.logger.error(f"Error inserting AES key and salt for {username}: {e}")
            raise

    def get_user_key_and_salt(self, username):
        """Retrieve the AES key and salt for a specific user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT aes_key, salt FROM {username}_keys ORDER BY created_at DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                return result[0], result[1]  # Return the AES key and salt
            return None, None
        except Exception as e:
            self.logger.error(f"Error retrieving AES key and salt for {username}: {e}")
            raise

    def get_user_key_id(self, username):
        """Retrieve the key ID for a specific user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT id FROM {username}_keys ORDER BY created_at DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the key ID
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving AES key ID for {username}: {e}")
            raise

    def insert_file_metadata(self, username, file_name, encrypted_path, key_id):
        """Insert file metadata for a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                INSERT INTO {username}_files (file_name, encrypted_path, key_id)
                VALUES (?, ?, ?)
            ''', (file_name, encrypted_path, key_id))
            self.conn.commit()
            self.logger.info(f"File metadata inserted for {file_name} in user {username}'s table.")
        except Exception as e:
            self.logger.error(f"Error inserting file metadata: {e}")
            raise

    def retrieve_file_metadata(self, username, file_name):
        """Retrieve metadata for a specific file."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {username}_files WHERE file_name=? AND delete_date IS NULL
            ''', (file_name,))
            file_metadata = cursor.fetchone()
            return file_metadata
        except Exception as e:
            self.logger.error(f"Error retrieving file metadata for {file_name}: {e}")
            raise

    def update_download_date(self, username, file_name):
        """Update the download date for a file."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                UPDATE {username}_files
                SET download_date=CURRENT_TIMESTAMP
                WHERE file_name=? AND delete_date IS NULL
            ''', (file_name,))
            self.conn.commit()
            self.logger.info(f"Download date updated for {file_name}.")
        except Exception as e:
            self.logger.error(f"Error updating download date: {e}")
            raise

    def mark_file_deleted(self, username, file_name):
        """Mark a file as deleted."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                UPDATE {username}_files
                SET delete_date=CURRENT_TIMESTAMP
                WHERE file_name=?
            ''', (file_name,))
            self.conn.commit()
            self.logger.info(f"File {file_name} marked as deleted.")
        except Exception as e:
            self.logger.error(f"Error marking file as deleted: {e}")
            raise
    def list_user_files(self, username):
        """List all metadata for current files of a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT id, file_name, encrypted_path, key_id, uploaded_at, download_date, shared_user
                FROM {username}_files 
                WHERE delete_date IS NULL
            ''')
            files = cursor.fetchall()
            
            # Convert the results to a list of dictionaries for easier handling
            file_list = []
            for file in files:
                file_dict = {
                    'id': file[0],
                    'file_name': file[1],
                    'encrypted_path': file[2],
                    'key_id': file[3],
                    'uploaded_at': file[4],
                    'download_date': file[5],
                    'shared_user': file[6]
                }
                file_list.append(file_dict)
            
            return file_list
        except Exception as e:
            self.logger.error(f"Error listing files for {username}: {e}")
            raise
    def list_all_users(self):
        """List all users in the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            users = cursor.fetchall()
            return [user[0] for user in users]
        except Exception as e:
            self.logger.error(f"Error listing all users: {e}")  

