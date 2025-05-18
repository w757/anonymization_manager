from dateutil import parser
import random
import string
from faker import Faker
from datetime import datetime, timedelta
from dateutil import parser


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
    print (value)
    print (data_category)
    
    if data_category in ["age", "height", "salary"]:
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

    if data_category == 'birth_date':
        print("a")
        return extract_year(value)

    elif data_category == 'postal_code':
        return value[:3] + 'XXX'  # np. 01XXX
    elif data_category == 'address':
        return value.split(',')[0]  # np. tylko ulica bez miasta
    elif data_category == 'phone':
        return value[:3] + 'XXXXXXX'
    elif data_category == 'email':
        return value.split('@')[0][:3] + '***@***'
   


# GENEROWANIE FALSZYWYCH DANYCH 
def fake_value (value, data_category):
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
    elif data_category == 'login':
        return fake.user_name()
    elif data_category == 'password':
        return fake.password()
    elif data_category == 'other':
        return "xxx"
    else:
        return "xxx"

# MASKOWANIE DANYCH 
def mask_value(value, data_category):
    return "***MASK***"