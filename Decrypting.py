from cryptography.fernet import Fernet

def decrypt_file(encrypted_path, decrypted_path, key):
    fernet = Fernet(key)
    with open(encrypted_path, 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"Decryption successful, saved as: {decrypted_path}")

if __name__ == "__main__":
    key = input("Enter your Fernet key: ").encode()  # user types key here
    encrypted_file = input("Enter the path of the encrypted file (e.g. file.txt.locked): ")
    decrypted_file = input("Enter the output path for decrypted file (e.g. file.txt): ")
    decrypt_file(encrypted_file, decrypted_file, key)
