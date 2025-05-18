
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib


import hashlib
from hashlib import pbkdf2_hmac

def hash_value(value, encryption_key, data_category):
    if not encryption_key:
        return "HASH_KEY_MISSING"
    salt = encryption_key[:16].encode()  # sól: pierwsze 16 znaków klucza
    hashed = pbkdf2_hmac('sha256', value.encode(), salt, 100000)
    return hashed.hex()


def encrypt_value(value, encryption_key, data_category):

    if not encryption_key:
        return "***ENCRYPTION_KEY_MISSING***"
    
    key = hashlib.sha256(encryption_key.encode()).digest()  # 32 bajty klucza AES
    iv = b'\x00' * 16  # ustalony wektor inicjalizujący (IV) - zawsze ten sam 

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(pad(value.encode(), AES.block_size))
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
    
    return encrypted_b64
