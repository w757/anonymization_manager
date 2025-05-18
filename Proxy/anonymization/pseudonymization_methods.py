
# from hashlib import pbkdf2_hmac
# from cryptography.fernet import Fernet
# import base64
# import hashlib
# from utils import validate_uuid
# from models import SwaggerAPI, Field

# # 🔑 Pobranie klucza szyfrowania z DB
# def get_encryption_key(service_uuid):
#     with app.app_context():
#         if not validate_uuid(service_uuid):
#             return None
#         swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
#         return swagger_api.encryption_key if swagger_api else None


# # 🔒 Szyfrowanie przy użyciu klucza
# def encrypt_value(value, encryption_key, data_category):
#     if not encryption_key:
#         return "***ENCRYPTION_KEY_MISSING***"
    
#     # Zakodowanie klucza w formacie odpowiednim dla Fernet (musi być 32 bajty -> 44 znaków base64)
#     key_bytes = hashlib.sha256(encryption_key.encode()).digest()
#     fernet_key = base64.urlsafe_b64encode(key_bytes[:32])
#     f = Fernet(fernet_key)

#     encrypted = f.encrypt(value.encode())
#     return encrypted.decode()



# # 🧂 Haszowanie z solą
# def hash_value(value, encryption_key, data_category):
#     if not encryption_key:
#         return "HASH_KEY_MISSING"

#     salt = encryption_key[:16].encode()  # użyj pierwszych 16 znaków klucza jako sól
#     hashed = pbkdf2_hmac('sha256', value.encode(), salt, 100000)
#     return hashed.hex()


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
    iv = b'\x00' * 16  # ustalony wektor inicjalizujący (IV) - zawsze ten sam, więc deterministyczny

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = cipher.encrypt(pad(value.encode(), AES.block_size))
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
    
    print(f"Encryption key: {key}")
    return encrypted_b64
