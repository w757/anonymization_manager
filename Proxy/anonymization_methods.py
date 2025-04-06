from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
import base64
import hashlib
from app import app
from utils import validate_uuid
from models import SwaggerAPI, Field

# 🔑 Pobranie klucza szyfrowania z DB
def get_encryption_key(service_uuid):
    with app.app_context():
        if not validate_uuid(service_uuid):
            return None
        swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
        return swagger_api.encryption_key if swagger_api else None


# 🔒 Szyfrowanie przy użyciu klucza
def encrypt_value(value, encryption_key, data_category):
    if not encryption_key:
        return "***ENCRYPTION_KEY_MISSING***"
    
    # Zakodowanie klucza w formacie odpowiednim dla Fernet (musi być 32 bajty -> 44 znaków base64)
    key_bytes = hashlib.sha256(encryption_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes[:32])
    f = Fernet(fernet_key)

    encrypted = f.encrypt(value.encode())
    return encrypted.decode()



# 🧂 Haszowanie z solą
def hash_value(value, encryption_key, data_category):
    if not encryption_key:
        return "HASH_KEY_MISSING"

    salt = encryption_key[:16].encode()  # użyj pierwszych 16 znaków klucza jako sól
    hashed = pbkdf2_hmac('sha256', value.encode(), salt, 100000)
    return hashed.hex()



def mask_value(value, data_category):
    return "***MASKED***"

def tokenize_value(value, data_category):
    return "***TOKENIZED***"

def redact_value(value, data_category):
    return "[REDACTED]"

def pseudonymize_value(value, data_category):
    return "PSEUDO-" + str(abs(hash(str(value))))


# 🔁 Główna funkcja
def apply_anonymization(value, method_name, service_uuid=None, data_category=None):
    methods = {
        "Masking": lambda v: mask_value(v, data_category),
        "Encryption": lambda v: encrypt_value(v, service_uuid, data_category),
        "Tokenization": lambda v: tokenize_value(v, data_category),
        "Redaction": lambda v: redact_value(v, data_category),
        "Pseudonymization": lambda v: pseudonymize_value(v, data_category),
        "Hashing": lambda v: hash_value(v, service_uuid, data_category)
    }
    
    if method_name not in methods:
        return value
        
    return methods[method_name](value)
