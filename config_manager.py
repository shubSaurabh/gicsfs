# config_manager.py
import json
import os
import logging

class ConfigManager:
    CONFIG_FILE = 'config.json'

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("SecureFileStorage")
        self.config = {}
        if os.path.exists(self.CONFIG_FILE):
            self.load_config()

    def load_config(self):
        """Load configuration from the config file."""
        try:
            with open(self.CONFIG_FILE, 'r') as file:
                self.config = json.load(file)
            self.logger.info("Configuration file loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading configuration file: {e}")
            raise

    def save_config(self):
        """Save configuration to the config file."""
        try:
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(self.config, file, indent=4)
            self.logger.info("Configuration file saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving configuration file: {e}")
            raise

    def get_client_id(self):
        """Retrieve the GitHub client ID from the configuration."""
        return self.config.get('client_id')

    def get_registration_complete(self):
        """Check if registration is complete."""
        if (self.config.get('client_id') and
            self.config.get('encrypted_client_secret') and
        self.config.get('storage_path') and
        self.config.get('salt') and
        self.config.get('registration_complete') == True):
            return True
        else:
            return False
        

    def set_client_id(self, client_id):
        """Store the GitHub client ID in the configuration."""
        self.config['client_id'] = client_id
        self.save_config()

    def get_encrypted_client_secret(self):
        """Retrieve the encrypted GitHub client secret from the configuration."""
        return self.config.get('encrypted_client_secret')

    def set_encrypted_client_secret(self, encrypted_secret):
        """Store the encrypted GitHub client secret in the configuration."""
        self.config['encrypted_client_secret'] = encrypted_secret
        self.save_config()

    def get_salt(self):
        """Retrieve the salt from the configuration."""
        return self.config.get('salt')

    def set_salt(self, salt):
        """Store the salt in the configuration."""
        self.config['salt'] = salt
        self.save_config()
    def get_storage_path(self):
        """Retrieve the storage path from the configuration."""
        return self.config.get('storage_path')

    def set_storage_path(self, storage_path):
        """Store the storage path in the configuration."""
        self.config['storage_path'] = storage_path
        self.save_config()
    def set_registration_complete(self, registration_complete):
        """Store the registration complete status in the configuration."""
        self.config['registration_complete'] = registration_complete
        self.save_config()

