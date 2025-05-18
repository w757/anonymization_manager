
from .anonymization_methods import add_noise_to_value, generalize_value, fake_value, mask_value
from .pseudonymization_methods import encrypt_value, hash_value



# Główna funkcja anonimizujaca/pseudonimizujaca
def apply_anonymization(value, method_name, service_uuid, data_category):
    print(f"method_name: {method_name} ({type(method_name)})")
    methods = {

        #pseudonimizacja
        "Encryption": lambda v: encrypt_value(v, service_uuid, data_category), 
        "Hashing": lambda v: hash_value(v, service_uuid, data_category),
        
        #anonimizacja:
        "Masking": lambda v: mask_value(v, data_category),
        "Aggregation": lambda v: aggregate_value(v, data_category),
        "Suppression": lambda v: suppress_value(v, data_category),
        "Generalization": lambda v: generalize_value(v, data_category)
    }
    

    # Zabezpieczenie przed błędnym typem
    if not isinstance(method_name, str):
        return value

    if method_name not in methods:
        return value

    return methods[method_name](value)
