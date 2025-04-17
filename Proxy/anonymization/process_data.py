
from .anonymization_methods import mask_value, aggregate_value, suppress_value, generalize_value
from .pseudonymization_methods import encrypt_value, hash_value



# 🔁 Główna funkcja
def apply_anonymization(value, method_name, service_uuid, data_category):
    methods = {

        #Pseudonymization
        "Encryption": lambda v: encrypt_value(v, service_uuid, data_category), 
        "Hashing": lambda v: hash_value(v, service_uuid, data_category),
        
        #Anonymization:
        "Masking": lambda v: mask_value(v, data_category),
        "Aggregation": lambda v: aggregate_value(v, data_category),
        "Suppression": lambda v: suppress_value(v, data_category),
        "Generalization": lambda v: generalize_value(v, data_category)
    }
    
    #print(methods)
    # if method_name not in methods:
    #     return value
        
    #return methods[method_name](value)

    # Debug info (można usunąć potem)
    #print(f"method_name: {method_name} ({type(method_name)})")

    # Zabezpieczenie przed błędnym typem
    if not isinstance(method_name, str):
        #print("⚠️ BŁĄD: method_name powinno być stringiem!")
        return value

    if method_name not in methods:
        #print(f"⚠️ Nieznana metoda: {method_name}")
        return value

    return methods[method_name](value)
