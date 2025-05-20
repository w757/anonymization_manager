
from .anonymization_methods import add_noise_to_value, generalize_value, fake_value, mask_value
from .pseudonymization_methods import encrypt_value, hash_value



# Główna funkcja anonimizujaca/pseudonimizujaca
def apply_anonymization(value, method_name, service_uuid, data_category):
    print(value, method_name, service_uuid, data_category)
    methods = {
        
        #pseudonimizacja
        "Encryption": lambda v: encrypt_value(v, service_uuid, data_category), 
        "Hashing": lambda v: hash_value(v, service_uuid, data_category),
        
        #anonimizacja:
        "Noise": lambda v: add_noise_to_value(v, data_category),
        "Generalization": lambda v: generalize_value(v, data_category),
        "Masking": lambda v: mask_value(v, data_category),
        "Fabrication": lambda v: fake_value(v, data_category),
        
    }
    

    # Zabezpieczenie przed błędnym typem
    if not isinstance(method_name, str):
        return value

    if method_name not in methods:
        return value

    return methods[method_name](value)
