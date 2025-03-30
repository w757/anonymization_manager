import json
from flask import Flask, request, make_response
import requests
from models import db, SwaggerAPI, Endpoint, Field, FieldAnonymization, AnonymizationMethod
import uuid


proxy_app = Flask(__name__)
proxy_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
proxy_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(proxy_app)

def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(str(uuid_to_test))
        return True
    except ValueError:
        return False

def get_target_api_url(service_uuid):
    with proxy_app.app_context():
        if not validate_uuid(service_uuid):
            return None
            
        swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
        return swagger_api.api_url if swagger_api else None

@proxy_app.before_request
def before_request():
    if request.method in ['POST', 'PUT', 'PATCH']:
        anonymize_request_data(request)

def anonymize_request_data(request):
    if request.is_json:
        try:
            data = request.get_json()
            anonymized_data = anonymize_data(data, request.path, request.method)
            request._cached_data = json.dumps(anonymized_data)
            request._parsed_content_type = 'application/json'
        except json.JSONDecodeError:
            pass

# def anonymize_response_data(response_data, path, method):
#     if isinstance(response_data, list):
#         print("*****")
#         return [anonymize_data(item, path, method) for item in response_data]
#     return anonymize_data(response_data, path, method

def anonymize_response_data(response_data, path, method):
    """
    Anonimizuje dane odpowiedzi API, obsługując różne struktury JSON:
    - Pojedyncze obiekty
    - Listy obiektów (np. lista użytkowników)
    - Zagnieżdżone obiekty
    """
    # Pobierz konfigurację endpointu z bazy danych
    endpoint_config = get_endpoint_config(path, method)
    
    if not endpoint_config:
        return response_data
        
    if isinstance(response_data, list):
        # Obsługa listy obiektów (np. GET /users zwracający listę)
        return [anonymize_item(item, endpoint_config) for item in response_data]
    elif isinstance(response_data, dict):
        # Obsługa pojedynczego obiektu lub zagnieżdżonej struktury
        return anonymize_item(response_data, endpoint_config)
    return response_data

def get_endpoint_config(path, method):
    """Pobiera konfigurację pól do anonimizacji dla danego endpointu"""
    with proxy_app.app_context():
        # Normalizuj ścieżkę dla porównania
        normalized_path = path.rstrip('/')
        
        # Znajdź endpoint z pełnym ładowaniem relacji
        endpoint = Endpoint.query.options(
            db.joinedload(Endpoint.fields)
              .joinedload(Field.anonymization)
              .joinedload(FieldAnonymization.anonymization_method)
        ).filter(
            db.or_(
                Endpoint.path == normalized_path,
                Endpoint.path == f"/{normalized_path.lstrip('/')}"
            ),
            Endpoint.method == method.upper()
        ).first()
        
        if not endpoint:
            print(f"No endpoint config found for {method} {path}")
            return None
            
        # Przygotuj słownik z polami do anonimizacji
        return {
            field.name: field.anonymization.anonymization_method.name
            for field in endpoint.fields
            if (field.is_response_field and 
                field.anonymization and 
                field.anonymization.anonymization_method)
        }

def anonymize_item(item, field_config):
    """Anonimizuje pojedynczy obiekt zgodnie z konfiguracją"""
    if not isinstance(item, dict):
        return item
        
    anonymized = {}
    for key, value in item.items():
        if key in field_config:
            # Anonimizuj pole jeśli jest w konfiguracji
            anonymized[key] = apply_anonymization(value, field_config[key])
        elif isinstance(value, dict):
            # Rekurencyjnie przetwarzaj zagnieżdżone obiekty
            anonymized[key] = anonymize_item(value, field_config)
        elif isinstance(value, list):
            # Przetwarzaj elementy listy
            anonymized[key] = [
                anonymize_item(i, field_config) if isinstance(i, dict) else i
                for i in value
            ]
        else:
            # Pozostaw bez zmian
            anonymized[key] = value
    return anonymized



def anonymize_data(data, path, method):
    with proxy_app.app_context():
        endpoint = Endpoint.query.filter_by(path=path, method=method.upper()).first()
        if endpoint:
            for field in endpoint.fields:
                if field.anonymization and field.anonymization.anonymization_method:
                    if isinstance(data, dict) and field.name in data:
                        data[field.name] = apply_anonymization(
                            data[field.name], 
                            field.anonymization.anonymization_method.name
                        )
        return data

def apply_anonymization(value, method):
    methods = {
        "Masking": "***MASKED***",
        "Encryption": "***ENCRYPTED***",
        "Tokenization": "***TOKENIZED***",
        "Redaction": "[REDACTED]",
        "Pseudonymization": "PSEUDO-" + str(abs(hash(str(value)))),
        "Hashing": "HASH-" + str(hash(str(value)))
    }
    return methods.get(method, value)

@proxy_app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@proxy_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(path):
    service_uuid = request.headers.get('X-Service-UUID')
    
    if not service_uuid:
        return make_response(
            json.dumps({
                "error": "Missing Service Identifier",
                "message": "X-Service-UUID header is required"
            }),
            400,
            {'Content-Type': 'application/json'}
        )
    
    target_api_url = get_target_api_url(service_uuid)
    
    if not target_api_url:
        return make_response(
            json.dumps({
                "error": "Invalid Service Configuration",
                "message": f"No API found for UUID: {service_uuid}"
            }),
            404,
            {'Content-Type': 'application/json'}
        )
    
    target_url = f"{target_api_url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers 
                    if key.lower() not in ['host', 'x-service-uuid']},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )
        

        if request.method == 'GET' and 'application/json' in response.headers.get('Content-Type', ''):
            try:
                response_data = response.json()
                
                
                anonymized_data = anonymize_response_data(response_data, path, request.method)
                
                # Debugowanie - wypisz oryginalne i anonimizowane dane
                # print("Original data:", response_data)
                print("Anonymized data:", anonymized_data)
                
                return make_response(
                    json.dumps(anonymized_data),
                    response.status_code,
                    dict(response.headers)
                )
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                pass
        
        return (response.content, response.status_code, response.headers.items())
    
    except requests.exceptions.RequestException as e:
        return make_response(
            json.dumps({
                "error": "Proxy Error",
                "message": str(e),
                "service_uuid": service_uuid,
                "target_url": target_url
            }),
            502,
            {'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    with proxy_app.app_context():
        db.create_all()
    proxy_app.run(port=5001, debug=True)