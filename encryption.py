# encryption.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import base64
import logging

class AESEncryptor:
    def __init__(self, password, salt, config_manager, logger=None):
        """Derive AES key from user password using PBKDF2 and store/retrieve salt."""
        self.logger = logger or logging.getLogger("SecureFileStorage")
        try:
            if config_manager is not None:
                salt = config_manager.get_salt()
            if not salt:
                salt = get_random_bytes(16)  # Generate a new salt
                if config_manager is not None:
                    config_manager.set_salt(base64.b64encode(salt).decode('utf-8'))
                self.logger.debug(f"New salt {salt} generated and stored in configuration.")
                self.logger.info("New salt generated and stored in configuration.")
            elif isinstance(salt, str):
                salt = base64.b64decode(salt.encode('utf-8'))
                self.logger.debug(f"Salt {salt} loaded from configuration and decoded.")
            else:
                self.logger.debug(f"Salt {salt} used as-is (assumed to be in bytes format).")

            self.key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
            self.block_size = AES.block_size
            self.logger.debug(f"AES encryption key derived successfully from user password.")
        except Exception as e:
            self.logger.error(f"Error during AES key derivation: {e}")
            raise

    def encrypt(self, plaintext):
        """Encrypt the plaintext using AES-GCM."""
        try:
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
            encrypted_text = base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')
            self.logger.debug(f"Encryption successful with ciphertext: {encrypted_text}")
            self.logger.info("Encryption successful.")
            return encrypted_text
        except Exception as e:
            self.logger.error(f"Error during encryption: {e}")
            raise

    def decrypt(self, encrypted_text):
        """Decrypt the ciphertext using AES-GCM."""
        try:
            decoded_data = base64.b64decode(encrypted_text.encode())
            nonce, tag, ciphertext = decoded_data[:self.block_size], decoded_data[self.block_size:self.block_size + 16], decoded_data[self.block_size + 16:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            decrypted_text = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
            self.logger.info("Decryption successful.")
            return decrypted_text
        except Exception as e:
            self.logger.error(f"Error during decryption: {e}")
            raise
    @staticmethod
    def generate_key_and_salt():
        """Generate a random AES key and salt."""
        try:
            key = get_random_bytes(32)  # AES-256 key (32 bytes)
            salt = get_random_bytes(16)  # Generate a new salt (16 bytes)
            return base64.b64encode(key).decode('utf-8'), base64.b64encode(salt).decode('utf-8')
        except Exception as e:
            logging.error(f"Error generating AES key and salt: {e}")
            raise
