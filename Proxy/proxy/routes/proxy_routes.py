import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Blueprint, request, make_response, current_app as app
import json
import requests
from services import get_target_api_url, anonymize_payload


proxy_bp = Blueprint('proxy', __name__)


# Request/response handlers
@proxy_bp.before_app_request
def before_request():
    """Anonymize incoming requests"""
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        content_type = request.content_type or ''
        
        # Handle JSON requests
        if 'application/json' in content_type and request.get_data():
            try:
                data = request.get_json()
                service_uuid = request.headers.get('X-Service-UUID')
                anonymized_data = anonymize_payload(app, data, request.path, request.method, is_response=False, service_uuid=service_uuid)
                request._cached_data = json.dumps(anonymized_data)
                request._parsed_content_type = 'application/json'
            except json.JSONDecodeError as e:
                print(f"Request JSON decode error: {e}")
        
        # Handle form data
        elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            form_data = request.form.to_dict()
            service_uuid = request.headers.get('X-Service-UUID')
            anonymized_data = anonymize_payload(app, form_data, request.path, request.method, is_response=False, service_uuid=service_uuid)
            request.form = anonymized_data



@proxy_bp.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@proxy_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(path):
    """Main proxy handler"""
    service_uuid = request.headers.get('X-Service-UUID')
    
    if not service_uuid:
        return make_response(
            json.dumps({"error": "Missing Service Identifier", 
                       "message": "X-Service-UUID header is required"}),
            400, {'Content-Type': 'application/json'})
    
    target_api_url = get_target_api_url(service_uuid, app)
    if not target_api_url:
        return make_response(
            json.dumps({"error": "Invalid Service Configuration",
                       "message": f"No API found for UUID: {service_uuid}"}),
            404, {'Content-Type': 'application/json'})
    
    target_url = f"{target_api_url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        # Prepare request data
        request_data = None
        if hasattr(request, '_cached_data'):
            request_data = request._cached_data
        elif request.get_data():
            request_data = request.get_data()
        
        # Forward request to target API
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers 
                    if key.lower() not in ['host', 'x-service-uuid']},
            data=request_data,
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )


        # Anonymize response if JSON
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/json' in content_type and response.content:
            try:
                response_data = response.json()
                service_uuid = request.headers.get('X-Service-UUID')  # Get service_uuid from request
                anonymized_data = anonymize_payload(app, 
                    response_data, path, request.method, is_response=True, service_uuid=service_uuid)  # Pass service_uuid here
                
                return make_response(
                    json.dumps(anonymized_data),
                    response.status_code,
                    dict(response.headers)
                )
            except (json.JSONDecodeError, ValueError) as e:
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