from dateutil import parser
import random
import string
from faker import Faker
from datetime import datetime, timedelta
from dateutil import parser
import re
import sys

def extract_year(date_string):
    try:
        # Parsowanie daty i wyodrębnienie roku
        parsed_date = parser.parse(date_string)
        return parsed_date.year
    except ValueError:
        return None  # Jeśli nie uda się sparsować daty

def noise_percent():
    return random.uniform(0.8, 1.2)

# DODAWANIE SZUMU DO DANYCH 
def add_noise_to_value(value, data_category):
    if data_category in ["age", "height", "salary"]:
        try:
            value = int(float(value))  
        except (ValueError, TypeError):
            return value  

        if isinstance(value, (int)): 
            return round(value * noise_percent())
        elif isinstance(value, (float)): 
            return round(value * noise_percent(),2)
    

    elif data_category == "birth_date":
            input_type = type(value)
            
            # Obsługa daty w postaci stringa
            if isinstance(value, str):
                try:
                    parsed_date = datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    return value  # niepoprawny format - zwróć bez zmian
            elif isinstance(value, datetime):
                parsed_date = value
            else:
                return value  # nieobsługiwany typ

            # Zakłócenie w zakresie 7–36 dni
            days_noise = round(random.uniform(-108, 108))
            noisy_date = parsed_date + timedelta(days=days_noise)

            # Zwróć w tym samym formacie, w jakim podano wejście
            return noisy_date.strftime("%Y-%m-%d") if input_type == str else noisy_date

    else:
        # Jeśli typ danych jest nieobsługiwany, zwróć oryginalną wartość
        return value 


# UOGOLNIENIE DANYCH
def generalize_value(value, data_category):
    if data_category == "age":
        try:
            value = int(float(value))  
        except (ValueError, TypeError):
            return value  

        if isinstance(value, (int, float)):
            return int(value // 10) * 10

    elif data_category == "birth_date":   
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return value
        if isinstance(value, datetime):
            return str(value.year)


    elif data_category == "postal_code":  
        if isinstance(value, str) and "-" in value:
            prefix = value.split("-")[0]
            return f"{prefix}-000"

    elif data_category == "salary":
        try:
            value = int(float(value))  
        except (ValueError, TypeError):
            return value  

        return int(value // 1000 + 1) * 1000

       
    elif data_category == "address":
        if isinstance(value, str):
            
            known_prefixes = r"(ul\.?|al\.?|plac|pl\.?|os\.?|skr\.?|nr\.?|blok|bud\.)"
            address = re.sub(rf"\b{known_prefixes}\b.*", "", value, flags=re.IGNORECASE).strip(", ").strip()

            city = address.split(",")[0].strip()

            if " " in city:
                city = city.split(" ")[0].strip()

            # Kapitalizacja
            return city.title()

    return value


# GENEROWANIE FAŁSZYWYCH DANYCH
def fake_value(value, data_category):
    # print(f"fals -> data_category: {data_category}, value: {value}", flush=True)  # DEBUG
    fake = Faker('pl_PL')

    if data_category == 'first_name':
        return fake.first_name()
    
    elif data_category == 'last_name':
        return fake.last_name()
    
    elif data_category == 'birth_date':
        new_birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
        return new_birth_date.isoformat()
    
    elif data_category == 'gender':
        return random.choice(['Male', 'Female', 'Other'])
    
    elif data_category == 'pesel':
        return fake.pesel()
    
    elif data_category == 'email':
        return fake.email()
    
    elif data_category == 'phone':
        return fake.phone_number()
    
    elif data_category == 'address':
        return fake.address().replace("\n", ", ")
    
    elif data_category == 'street':
        return fake.street_name()
    
    elif data_category == 'postal_code':
        return fake.postcode()
    
    elif data_category == 'city':
        return fake.city()
    
    elif data_category == 'country':
        return fake.country()
    
    elif data_category == 'password':
        return fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    
    elif data_category == 'age':
        return random.randint(18, 90)
    
    elif data_category == 'height':
        return round(random.uniform(150.0, 200.0), 1)  # wzrost w cm
    
    elif data_category == 'salary':
        return round(random.uniform(3000.0, 20000.0), 2)  # wynagrodzenie
    
    elif data_category == 'login':
        return fake.user_name()
    
    elif data_category == 'other':
        return "xxx"
    
    else:
        return "xxx"


# MASKOWANIE DANYCH 
def mask_value(value, data_category):
    # print(f"mask -> data_category: {data_category}, value: {value}", flush=True)  # DEBUG
    if isinstance(value, str):
        masked = ''
        for char in value:
            if char.isalpha():
                masked += 'x'
            elif char.isdigit():
                masked += '0'
            else:
                masked += char  # zachowaj znaki specjalne, spacje, przecinki itp.
        return masked

    elif isinstance(value, int):
        return int('0' * len(str(value)))

    elif isinstance(value, float):
        # Zamaskuj część całkowitą i dziesiętną oddzielnie, zachowując strukturę
        value_str = f"{value:.2f}"
        masked = ''.join(['0' if c.isdigit() else c for c in value_str])
        return float(masked)

    return "****"  # dla innych typów danych jako fallback
