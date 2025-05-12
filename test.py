# import random
# import string
# from faker import Faker
# from datetime import datetime
# from dateutil import parser
# import random
# import string
# from faker import Faker
# from dateutil import parser

# fake = Faker('pl_PL')

# def mask_value(value, data_category):
#     if data_category == 'first_name':
#         return fake.first_name()
#     elif data_category == 'last_name':
#         return fake.last_name()
#     elif data_category == 'birth_date':
#         parsed_date = parser.parse(value)
#         year_offset = random.randint(-5, 5)
#         new_birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
#         new_birth_date = new_birth_date.replace(year=parsed_date.year + year_offset)
#         return new_birth_date.isoformat()
#     elif data_category == 'gender':
#         return random.choice(['Male', 'Female', 'Other'])
#     elif data_category == 'pesel':
#         return fake.pesel()
#     elif data_category == 'email':
#         return fake.email()
#     elif data_category == 'phone':
#         return fake.phone_number()
#     elif data_category == 'address':
#         return fake.address().replace("\n", ", ")
#     elif data_category == 'street':
#         return fake.street_name()
#     elif data_category == 'postal_code':
#         return fake.postcode()
#     elif data_category == 'city':
#         return fake.city()
#     elif data_category == 'country':
#         return fake.country()
#     elif data_category == 'login':
#         return fake.user_name()
#     elif data_category == 'password':
#         return fake.password()
#     elif data_category == 'other':
#         return "xxx"
#     else:
#         return "xxx"

# def mask_data(data):
#     masked_data = {}
    
#     for data_category, value in data.items():
#         masked_data[data_category] = mask_value(value, data_category)

#     return masked_data

# # Przykład użycia
# data_example = {
#     'first_name': 'John',
#     'last_name': 'Doe',
#     'birth_date': '10/12/2000',
#     'gender': 'Male',
#     'pesel': '12345678901',
#     'email': 'john.doe@example.com',
#     'phone': '123456789',
#     'address': '123 Main St',
#     'street': 'Main St',
#     'postal_code': '12-345',
#     'city': 'Sample City',
#     'country': 'Sample Country',
#     'login': 'john_doe',
#     'password': 'securepassword',
#     'other': 'Some other info'
# }

# masked_data = mask_data(data_example)
# print(masked_data)


import random
from faker import Faker
from datetime import datetime
from dateutil import parser

fake = Faker('pl_PL')

def extract_year(date_string):
    try:
        parsed_date = parser.parse(date_string)
        return parsed_date.year
    except ValueError:
        return None

def generalize_value(value, data_category):
    try:
        if data_category == 'first_name':
            return value[0] + '.'  # Jan -> J.

        elif data_category == 'last_name':
            return value[0] + '.'  # Kowalski -> K.

        elif data_category == 'birth_date':
            return extract_year(value)

        elif data_category == 'gender':
            return 'Unknown'

        elif data_category == 'pesel':
            return value[:2] + '********'

        elif data_category == 'email':
            local = value.split('@')[0][:3]
            return f"{local}***@***"

        elif data_category == 'phone':
            return value[:3] + 'XXXXXXX'

        elif data_category == 'address':
            return value.split(',')[0].strip()

        elif data_category == 'street':
            return value.split()[0]

        elif data_category == 'postal_code':
            return value[:2] + 'XXX'

        elif data_category == 'city':
            return "województwo"

        elif data_category == 'country':
            return "Europa"

        elif data_category == 'login':
            return value[:3] + '***'

        elif data_category == 'password':
            return '***'

        elif data_category == 'other':
            return 'zgeneralizowane'

        else:
            return 'zgeneralizowane'
    except Exception:
        return 'błąd_generalizacji'

def generalize_data(data):
    generalized_data = {}
    for data_category, value in data.items():
        generalized_data[data_category] = generalize_value(value, data_category)
    return generalized_data

# Przykładowe dane wejściowe
data_example = {
    'first_name': 'John',
    'last_name': 'Doe',
    'birth_date': '2000-12-10',
    'gender': 'Male',
    'pesel': '12345678901',
    'email': 'john.doe@example.com',
    'phone': '+48123456789',
    'address': 'ul. Przykładowa 123, Warszawa',
    'street': 'Przykładowa 123',
    'postal_code': '01-234',
    'city': 'Warszawa',
    'country': 'Polska',
    'login': 'john_doe',
    'password': 'securepassword',
    'other': 'Jakieś dodatkowe dane'
}

generalized_data = generalize_data(data_example)
print(generalized_data)
