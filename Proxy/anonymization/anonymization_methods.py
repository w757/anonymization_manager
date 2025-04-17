from dateutil import parser


def extract_year(date_string):
    try:
        # Parsowanie daty i wyodrębnienie roku
        parsed_date = parser.parse(date_string)
        return parsed_date.year
    except ValueError:
        return None  # Jeśli nie uda się sparsować daty



def mask_value(value, data_category):
    return "***mask_value***"

def aggregate_value(value, data_category):
    return "***aggregate_value***"

def suppress_value(value, data_category):
    return "***suppress_value***"

def generalize_value(value, data_category):
    #logging.info(f"Próba parsowania daty: {value}")
    #def generalize_value(value, data_category):
    
    
    if data_category == 'birth_date':
        print("a")
        extract_year(value)

    elif data_category == 'postal_code':
        return value[:2] + 'XXX'  # np. 01XXX
    elif data_category == 'address':
        return value.split(',')[0]  # np. tylko ulica bez miasta
    elif data_category == 'phone':
        return value[:3] + 'XXXXXXX'
    elif data_category == 'email':
        return value.split('@')[0][:3] + '***@***'
   