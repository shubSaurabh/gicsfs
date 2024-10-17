# GIC's Secure File Storage
Author: Shubham Saurabh
mail: shub_sau@live.com

## Introduction

This is a CLI based secure file storage system that uses AES encryption to encrypt and decrypt files and stores them on user's local machine. 

## Architecture

### Components:

1. CLI - Command Line Interface
2. Github OAuth authorization code flow - Authorization code flow is used to authenticate the user.
3. Database - sqllite3 encrypted using SQLiteCipher
4. File operations


This system's requirments had a fundamental missing block, which was how to secure user's keys and all the metadata itself. Oauth authentication can only authorize a user, however, we needed to protect CLI too as it is a shared component. To solve this problem i have added an additional layer of protection using 'master password' This, master password is used for following:
1. To derive a key which will be used to secure access to database.
2. All user's will have to authenticate themselves with master password to access the CLI. This will divide access management into two parts, one at the CLI level and other at file operation level. Access to CLI itself is restricted, and then access to files is authorised using github oauth flow.

Furthermore, this system is built with strong access management principles and secures data and access to it at every level. For instance:

1. Although its a multi user system, a user can only access its own files, and no other user's files. 
2. Each user's data is encrypted using their own unique key, using AES encryption algorithm, which is stored in the database. No operation allows access to keys, and any access to database needs master password and oauth flow.
3. Github token is only stored in memory which is released the moment user exits the CLI.
4. All user related data is stored in a json file, and client secret is also encrypted using key derived from master password.
5. CLI is completely based on python, it uses only standard libraries. It uses sqlite3 to store the user's data and github oauth authorization code flow to authenticate the user. it uses encrypted version of sqllite3, SQLiteCipher to encrypt and decrypt the database. 

Each user will have two tables, one for storing file metadata including sharing details and other for storing key. Each user will have unique key and salt for file encryption, therefore two users CANNOT decrypt each other's files.

## Usage

```
python cli.py 
```

This will start the program, it has following options:

1. Register
2. Admin
3. Login
4. Exit

### Permissions needed and file structure

1. You can create a directory anywhere on the system and clone the repo
2. run the above command to start the CLI, it needs python version 3.6 or above
3. It will ask for master password, this is the password for the master password, it is used to authenticate the user and to derive a key to encrypt and decrypt the user's data.
4. It will ask for github client ID and client secret, this is used to authorize the user. User will have to setup github oauth app, and will have client ID and client secret. This is used to authorize the user. User will have to paste the client ID and client secret in the CLI. That can be done by logging into their github account and then navigating to user's setting (by clicking on the top right corner dropdown). Then navigating to "Developer settings" -> "OAuth Apps" -> "New OAuth App". Then they will have to fill the required fields and will get their client ID and client secret. App name can be anything, homepage and authorization callback URL MUST be https://localhost, this is the default callback URL for the CLI and because CLI is not running on any web server.
5. All file paths including storage path shoould be absolute paths. Otherwise system will try to access the files in the current working directory of the CLI.
6. After this the user will be asked to login, this is done using Github OAuth authorization code flow. It will redirect to Github for authorization and then back to the CLI. User will be asked to either click a github URL or paste it in any browser, this is because this CLI is created with an assumption that user is running it on a machine which does not have a browser (preferably a linux terminal). If a user has a browser, then all they need to do is click on the URL which will open github authentication page and then redirect to a custom URL with auth code it should look like https://localhost/?code=<code>&state=<state>. Paste this URL back in CLI and they will be logged in. 


### Github OAuth authorization code flow

User will have to setup github oauth app, and will have client ID and client secret. This is used to authorize the user. User will have to paste the client ID and client secret in the CLI. That can be done by logging into their github account and then navigating to user's setting (by clicking on the top right corner dropdown). Then navigating to "Developer settings" -> "OAuth Apps" -> "New OAuth App". Then they will have to fill the required fields and will get their client ID and client secret. App name can be anything, homepage and authorization callback URL MUST be https://localhost, this is the default callback URL for the CLI and because CLI is not running on any web server.

### Register

This is used to setup the CLI for the first time, it will ask for the master password and the master password is used to derive a key from the user's master password and the salt is stored in the database. Since we need to secure user's keys, and all user related data it is done using a master password. Which means that user's data is not at all accessible to anyone including the user himself without the master password. Master password is also used to authenticate whether a user is authorized to access the secure file storage or not. Only after this, a user can then move on to login.

### Admin

This functionality is added to reset the CLI for a new oauth app, however if master password is changed old files will not be accessible. In case master password is forgotten there is no way to recover it, that would be an improvement and is not added as of now. Admin allows to re-register, which will delete the database and configurations but not the encrypted files. However deleting database will mean encrypted files also cannot be recovered as keys will be lost. Admin can be used to list all users too, however an admin CANNOT access any user's files. 

### Login

This is used to login to the secure file storage. It works with Github OAuth authorization code flow. It will redirect to Github for authorization and then back to the CLI. User will be asked to either click a github URL or paste it in any browser, this is because this CLI is created with an assumption that user is running it on a machine which does not have a browser (preferably a linux terminal). If a user has a browser, then all they need to do is click on the URL which will open github authentication page and then redirect to a custom URL with auth code it should look like https://localhost/?code=<code>&state=<state>. Paste this URL back in CLI and they will be logged in. 

Each user will have to provide master password and go through a github login process to access file operations. Following are the file operations:

1. Upload a file - User can upload a file to the secure file storage.
2. Download a file - User can download a file from the secure file storage.
3. Delete a file - User can delete a file from the secure file storage.
4. List all files - User can list all files in the secure file storage. it will return a list of files with file names and other details. deleted files will not be shown.
5. Share a file with other users - User can share a file with other users. it can be one user or multiple users separated by comma. Usernames should be the username of the github user. If a new list is provided, it will overwrite the existing list of users, so make sure to add all the users again.
6. Unshare a file with other users - User can unshare a file with all users using the unshare_all command.
7. List all users - Admin can list all users in the secure file storage. this is limited to admin only.

## Dependencies and Installation

This project requires both Python packages and system-level dependencies. Follow these steps to set up your environment:

### System Dependencies

Before installing the Python packages, you need to install the following system-level dependencies:

- sqlcipher
- libsqlcipher0
- libsqlcipher-dev

On Ubuntu or Debian-based systems, you can install these using apt:

```bash
sudo apt update
sudo apt install sqlcipher libsqlcipher0 libsqlcipher-dev
```

For other operating systems, please refer to the SQLCipher documentation for installation instructions.

### Python Dependencies

After installing the system dependencies, you can install the required Python packages using pip:

1. First, ensure you have pip installed and updated:
   ```bash
   python -m pip install --upgrade pip
   ```

2. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

This will install the following Python packages:
- requests: For making HTTP requests
- requests-oauthlib: For handling OAuth 2.0 authentication
- pycryptodome: For encryption and decryption operations
- pysqlcipher3: Python bindings for SQLCipher IMPORTANT NOTE: This package is only available after the above mentioned system dependencies are installed. In case you see an error saying that pysqlcipher3 is not installed, it means that the system dependencies are not installed. install the system dependencies first and then pip install pysqlcipher3 again. 

### Note on Virtual Environments

It's recommended to use a virtual environment for this project. You can create one using:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Then proceed with the pip installation as described above.

If you encounter any issues during installation, please check that all system dependencies are correctly installed and that you're using a compatible Python version (3.6+).

## Implementation Details

Cli is the entry point for the program. It is a console based interface that allows users to interact with the program.

### Db_manager
This module manages the database. It has following methods:

1. create_tables
2. add_user
3. get_user_key_and_salt
4. store_file_metadata
5. retrieve_file_metadata   
6. update_shared_users
7. get_shared_file_metadata

### File_ops
This module contains the logic for the file operations. It has following methods:

1. upload
2. download
3. delete
4. list_files   
5. share
6. unshare_all
7. download_shared_file

### Logger
This module that is used to log the messages to a file. It is used to log the messages to a file. this is where log level can be changed. DEBUG will print senstive information like github oauth flow details and INFO will print other details.

### auth.py 
This module contains the logic for the authentication using Github OAuth authorization code flow.

### cli.py  
This module is the entry point for the program. It is the first module that is executed. It contains the main logic for the program. It uses the PyCryptodome library for encryption and decryption.

### Testing

Since this is a CLI based application, testing is done manually. However i have added comments in the code to make it more readable and understandable. Once setup is done, following test cases can be run:

1. Register a new user and login with that user.
2. Upload a file and list all files and check if the file is uploaded.
3. Download a file and check if the file is downloaded.
4. Delete a file and check if the file is deleted.
5. Share a file with other users and check if the file is shared.
6. Unshare a file with other users and check if the file is unshared.
7. List all users and check if the users are listed.
