#GIC's Secure File Storage

This is a secure file storage system that uses AES encryption to encrypt and decrypt files.

It uses the PyCryptodome library for encryption and decryption.

It uses the SQLite library for the database.

It uses the SQLite Cipher library for the database.


it allows users to upload, download, delete, and list files.

it allows users to share files with other users.

it allows users to unshare files with other users.

it allows users to list all files in the system.

it allows users to list all users in the system.

If same file is uploaded twice, it will be stored only once in the database and the path will be the same. 

Files will be encrypted with a random AES key and the key is stored in the database. The master password is used to derive a key from the user's master password and the salt is stored in the database.




