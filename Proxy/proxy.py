import json
from flask import Flask, request, make_response
import requests
from models import db, SwaggerAPI, Endpoint, Field, FieldAnonymization, AnonymizationMethod
import uuid
from sqlalchemy.orm import joinedload
from anonymization_methods import apply_anonymization

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Helper functions
def validate_uuid(uuid_to_test):
    try:
        uuid.UUID(str(uuid_to_test))
        return True
    except ValueError:
        return False

def get_target_api_url(service_uuid):
    with app.app_context():
        if not validate_uuid(service_uuid):
            return None
        swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
        return swagger_api.api_url if swagger_api else None

# def apply_anonymization(value, method):
#     methods = {
#         "Masking": "***MASKED***",
#         "Encryption": "***ENCRYPTED***",
#         "Tokenization": "***TOKENIZED***",
#         "Redaction": "[REDACTED]",
#         "Pseudonymization": "PSEUDO-" + str(abs(hash(str(value)))),
#         "Hashing": "HASH-" + str(hash(str(value)))
#     }
#     return methods.get(method, value)

def get_endpoint_config(path, method, is_response):
    """Get anonymization config for endpoint"""
    with app.app_context():
        endpoint = Endpoint.query.options(
            joinedload(Endpoint.fields)
            .joinedload(Field.anonymization)
            .joinedload(FieldAnonymization.anonymization_method)
        ).filter(
            db.or_(
                Endpoint.path == path.rstrip('/'),
                Endpoint.path == '/' + path.lstrip('/')
            ),
            Endpoint.method == method.upper()
        ).first()

        if not endpoint:
            return None
            
        return {
            field.name: field.anonymization.anonymization_method.name
            for field in endpoint.fields
            if (field.is_response_field == is_response and
                field.anonymization and
                field.anonymization.anonymization_method)
        }

def anonymize_item(item, field_config):
    """Anonymize single item according to config"""
    if not isinstance(item, dict):
        return item
        
    anonymized = {}
    for key, value in item.items():
        if key in field_config:
            anonymized[key] = apply_anonymization(value, field_config[key])
        elif isinstance(value, dict):
            anonymized[key] = anonymize_item(value, field_config)
        elif isinstance(value, list):
            anonymized[key] = [anonymize_item(i, field_config) if isinstance(i, dict) else i 
                            for i in value]
        else:
            anonymized[key] = value
    return anonymized

def anonymize_payload(data, path, method, is_response):
    """Main anonymization function for both requests and responses"""
    endpoint_config = get_endpoint_config(path, method, is_response)
    if not endpoint_config:
        return data
        
    if isinstance(data, list):
        return [anonymize_item(item, endpoint_config) for item in data]
    elif isinstance(data, dict):
        return anonymize_item(data, endpoint_config)
    return data

# Request/response handlers
@app.before_request
def before_request():
    """Anonymize incoming requests"""
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            data = request.get_json()
            anonymized_data = anonymize_payload(data, request.path, request.method, is_response=False)
            request._cached_data = json.dumps(anonymized_data)
            request._parsed_content_type = 'application/json'
        except json.JSONDecodeError as e:
            print(f"Request JSON decode error: {e}")

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(path):
    """Main proxy handler"""
    service_uuid = request.headers.get('X-Service-UUID')
    
    if not service_uuid:
        return make_response(
            json.dumps({"error": "Missing Service Identifier", 
                       "message": "X-Service-UUID header is required"}),
            400, {'Content-Type': 'application/json'})
    
    target_api_url = get_target_api_url(service_uuid)
    if not target_api_url:
        return make_response(
            json.dumps({"error": "Invalid Service Configuration",
                       "message": f"No API found for UUID: {service_uuid}"}),
            404, {'Content-Type': 'application/json'})
    
    target_url = f"{target_api_url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        # Forward request to target API
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

        # Anonymize response if JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                response_data = response.json()
                anonymized_data = anonymize_payload(
                    response_data, path, request.method, is_response=True)
                
                return make_response(
                    json.dumps(anonymized_data),
                    response.status_code,
                    dict(response.headers)
                )
            except json.JSONDecodeError as e:
                print(f"Response JSON decode error: {e}")
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
    with app.app_context():
        db.create_all()
    app.run(port=5001, debug=True)