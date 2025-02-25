from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import Config
import base64

# Clé de chiffrement
key = base64.b64decode(Config.ENCRYPTION_KEY)

# Fonction de chiffrement du nom
def encrypt_username(username):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_username = pad(username.encode(), AES.block_size)
    encrypted_username = cipher.encrypt(padded_username)
    return base64.b64encode(encrypted_username).decode()

# Fonction de déchiffrement du nom
def decrypt_username(encrypted_username):
    cipher = AES.new(key, AES.MODE_ECB)
    decoded_encrypted_username = base64.b64decode(encrypted_username)
    decrypted_username = unpad(cipher.decrypt(decoded_encrypted_username), AES.block_size)
    return decrypted_username.decode()