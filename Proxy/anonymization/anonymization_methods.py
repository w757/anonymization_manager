from dateutil import parser
import random
import string
from faker import Faker
from datetime import datetime
from dateutil import parser


def extract_year(date_string):
    try:
        # Parsowanie daty i wyodrębnienie roku
        parsed_date = parser.parse(date_string)
        return parsed_date.year
    except ValueError:
        return None  # Jeśli nie uda się sparsować daty






# DODAWANIE SZUMU DO DANYCH 
def add_noise_to_value(value, data_category):
    return "***add_noise_to_value***"


# UOGOLNIENIE DANYCH
def generalize_value(value, data_category):

    if data_category == 'birth_date':
        print("a")
        return extract_year(value)

    elif data_category == 'postal_code':
        return value[:2] + 'XXX'  # np. 01XXX
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