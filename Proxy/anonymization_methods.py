def mask_value(value):
    """Masking sensitive data with asterisks"""
    return "***MASKED***"

def encrypt_value(value):
    """Simulate encryption (in real implementation use proper crypto)"""
    return "***ENCRYPTED***"

def tokenize_value(value):
    """Simulate tokenization"""
    return "***TOKENIZED***"

def redact_value(value):
    """Complete redaction of data"""
    return "[REDACTED]"

def pseudonymize_value(value):
    """Pseudonymization with hash"""
    return "PSEUDO-" + str(abs(hash(str(value))))

def hash_value(value):
    """Simple hashing"""
    return "HASH-" + str(hash(str(value)))

def apply_anonymization(value, method_name):
    """Main function to apply specific anonymization method"""
    methods = {
        "Masking": mask_value,
        "Encryption": encrypt_value,
        "Tokenization": tokenize_value,
        "Redaction": redact_value,
        "Pseudonymization": pseudonymize_value,
        "Hashing": hash_value
    }
    
    if method_name not in methods:
        return value
        
    return methods[method_name](value)