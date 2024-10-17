# cli.py
import argparse
from encryption import AESEncryptor
from file_ops import FileManager
from config_manager import ConfigManager
from db_manager import SQLiteManager
from logger import Logger
from auth import GitHubAuth
import requests
import os
import sys
from pysqlcipher3 import dbapi2 as sqlite
import getpass

def prompt_for_github_client_id():
    return input("Enter GitHub Client ID: ")

def prompt_for_github_client_secret():
    return getpass.getpass("Enter GitHub Client Secret: ")

def prompt_for_master_password():
    return getpass.getpass("Enter your master password: ")

def prompt_for_storage_path():
    return input("Enter the storage path: ")

def validate_access_token(token):
    """Validate the GitHub OAuth access token by checking it with GitHub's API."""
    url = "https://api.github.com/user"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    return response

def setup_database(master_password, logger):
    db_path = 'storage.db'
    try:
        conn = sqlite.connect(db_path)
        conn.execute(f"PRAGMA key = '{master_password}'")
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt TEXT, aes_key TEXT)")
        conn.close()
        logger.info("Database setup completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False

def main():
    logger = Logger('GICSFS-CLI.log').logger
    config_manager = ConfigManager(logger)

    # Continuous CLI session
    
    
    while True:
        if config_manager.get_registration_complete() == False:
            print("\nWelcome to GIC's Secure File Storage CLI")
            print("Type 'register' to register the application, or type 'exit' to quit.")
            print("Disclaimer: This code is written by Shubham Saurabh as part of an interview assessment exercise by GIC and is not intended to be used for any other purpose. Enjoy!")
            user_input = input("GICSFS> ").strip().lower()
            
            if user_input == 'exit':
                print("Exiting the CLI session. Thank you for using GIC's Secure File Storage CLI!")
                break
        
             
            try:
                if user_input == 'register':
                    # Registration process
                    if config_manager.get_registration_complete() == True:
                        print("Registration already completed. Please proceed to the next step.")
                        continue

                    master_password = prompt_for_master_password()
                    if setup_database(master_password, logger):
                        salt = AESEncryptor.generate_key_and_salt()
                        config_manager.set_salt(salt[1])
                        
                        github_client_id = prompt_for_github_client_id()
                        config_manager.set_client_id(github_client_id)
                        
                        github_client_secret = prompt_for_github_client_secret()
                        encryptor = AESEncryptor(master_password, salt[1], config_manager, logger)
                        encrypted_client_secret = encryptor.encrypt(github_client_secret)
                        config_manager.set_encrypted_client_secret(encrypted_client_secret)
                        
                        storage_path = prompt_for_storage_path()
                        config_manager.set_storage_path(storage_path)
                        
                        print("Registration completed successfully.")
                        logger.info("Registration completed successfully.")
                        config_manager.set_registration_complete(True)
                    else:
                        print("Registration failed. Please try again.")
                    continue
                else:
                    print("Invalid command. Only acceptable commands are 'register' or 'exit'.")
                    logger.error("Invalid command. Only acceptable commands are 'register' or 'exit'.")
                    config_manager.set_registration_complete(False)
                    sys.exit(1)
            except Exception as e:
                print(f"Error during registration: {e}")
                logger.error(f"Error during registration: {e}")
                os.remove('storage.db')
                os.remove('config.json')
                config_manager.set_registration_complete(False)
                sys.exit(1)
        else:
            print("\nWelcome to GIC's Secure File Storage CLI")
            print("You are already registered. Please proceed with your master password to proceed.")
            print("Type admin to enter admin mode, or just press enter to proceed as a normal user.")
            user_input = input("GICSFS> ").strip().lower()
            if user_input == 'exit':
                print("Exiting the session.")
                break

            if user_input == 'admin':
                print("Admin mode enabled.")
                # Add admin mode functionality here
                print("What would you like to do? Type re-register to re-register the application, type list-users to list all users, or type exit to quit.")
                user_input = input("GICSFS> ").strip().lower()
                if user_input == 're-register':
                    print("Re-registering the application.")
                    os.remove('storage.db')
                    os.remove('config.json')
                    config_manager.set_registration_complete(False)
                    continue
                elif user_input == 'list-users':
                    print("Listing all users.")
                    db_manager = SQLiteManager('storage.db', logger)
                    print(db_manager.list_all_users())
                    continue   
                elif user_input == 'exit':
                    print("Exiting the session.")
                    break
            else:
                # Prompt for master password for normal operations
                master_password = prompt_for_master_password()
                if master_password == 'exit':
                    print("Exiting the session.")
                    break
            

            # Initialize the encryptor with the master password and load GitHub credentials from config
            encryptor = AESEncryptor(master_password, config_manager.get_salt(), config_manager, logger)

            client_id = config_manager.get_client_id()
            encrypted_client_secret = config_manager.get_encrypted_client_secret()
            client_secret = encryptor.decrypt(encrypted_client_secret)

            # Connect to the database
            try:
                db_manager = SQLiteManager('storage.db', logger)
                db_manager.connect(master_password)
            except Exception as e:
                print(f"Failed to connect to the database: {e}")
                logger.error(f"Database connection failed: {e}")
                continue

            # Perform GitHub OAuth once, at the start of the session
            github_auth = GitHubAuth(client_id, client_secret, logger)
            try:
                access_token = github_auth.authenticate()
                logger.info("GitHub OAuth authentication successful.")
            except Exception as e:
                print(f"GitHub authentication failed: {e}")
                logger.error(f"GitHub authentication failed: {e}")
                db_manager.conn.close()  # Close the database connection before continuing
                continue  # If authentication fails, restart loop

            # Validate the access token
            response = validate_access_token(access_token)
            logger.info(f"Access token validation response: {response.status_code}")

            if response.status_code != 200:
                print("Invalid access token. Please try again.")
                db_manager.conn.close()  # Close the database connection before continuing
                continue

            username = response.json()['login']
            storage_path = config_manager.get_storage_path()
            file_manager = FileManager(storage_path, db_manager, logger)
            print(f"Authenticated as {username}. You can now upload, download, list, or delete files. Type 'exit' to quit.")

            while True:
                operation_input = input("Enter command (upload, download, list, delete, exit): ").strip().lower()

                if operation_input == 'exit':
                    print("Exiting the session.")
                    db_manager.conn.close()  # Close the database connection
                    break

                try:
                    if operation_input == 'upload':
                        file_path = input("Enter the path to the file: ").strip()
                        file_manager.upload(username, file_path)
                    elif operation_input == 'download':
                        filename = input("Enter the filename to download: ").strip()
                        file_manager.download(username, filename)
                    elif operation_input == 'delete':
                        filename = input("Enter the filename to delete: ").strip()
                        file_manager.delete(username, filename)
                    elif operation_input == 'list':
                        file_manager.list_files(username)
                    else:
                        print("Invalid command. Please enter 'upload', 'download', 'list', 'delete', or 'exit'.")
                except Exception as e:
                    print(f"Error during operation: {e}")
                    logger.error(f"Error during operation: {e}")

            # If we break out of the loop, ensure the database connection is closed
            if db_manager and db_manager.conn:
                db_manager.conn.close()

if __name__ == "__main__":
    main()
