import json
from flask import Flask, request, make_response
import requests
from models import db, SwaggerAPI, Endpoint, FieldAnonymization
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

def anonymize_data(data, path, method):
    with proxy_app.app_context():
        endpoint = Endpoint.query.filter_by(path=path, method=method.upper()).first()
        if endpoint:
            for field in endpoint.fields:
                if field.name in data and field.anonymization and field.anonymization.anonymization_method:
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