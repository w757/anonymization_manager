import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json
from sqlalchemy.orm import joinedload
from common.extensions import db
from common.models import SwaggerAPI, Endpoint, Field, FieldAnonymization
from anonymization.process_data import apply_anonymization
from utils import validate_uuid


def get_target_api_url(service_uuid, app):
    with app.app_context():
        if not validate_uuid(service_uuid):
            return None
        swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
        return swagger_api.api_url if swagger_api else None


def get_endpoint_config(app, path, method, is_response):
    """Get anonymization config for endpoint"""
    with app.app_context():

        base_path = path.split('?')[0].rstrip('/')
        
        endpoint = Endpoint.query.options(
            joinedload(Endpoint.fields)
            .joinedload(Field.anonymization)
            .joinedload(FieldAnonymization.anonymization_method)
        ).filter(
            db.or_(
                Endpoint.path == base_path,
                Endpoint.path == '/' + base_path.lstrip('/')
            ),
            Endpoint.method == method.upper()
        ).first()

        print(endpoint)

        if not endpoint:
            return None
            
        return {
            field.name: field.anonymization.anonymization_method.name
            for field in endpoint.fields
            if (field.is_response_field == is_response and
                field.anonymization and
                field.anonymization.anonymization_method)
        }



def anonymize_item(item, field_config, service_uuid, path, method, is_response):
    if not isinstance(item, dict):
        return item

    anonymized = {}

    swagger_api = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
    encryption_key = swagger_api.encryption_key if swagger_api else None
   
    for key, value in item.items():
        if key in field_config:
            data_category = get_data_category(service_uuid, path, method, key, is_response)
            print(data_category)
            anonymized[key] = apply_anonymization(value, field_config[key], encryption_key, data_category)

        elif isinstance(value, dict):
            anonymized[key] = anonymize_item(value, field_config, service_uuid, path, method, is_response)
        elif isinstance(value, list):
            anonymized[key] = [
                anonymize_item(i, field_config, service_uuid, path, method, is_response) if isinstance(i, dict) else i
                for i in value
            ]
        else:
            anonymized[key] = value

    return anonymized



def anonymize_payload(app, data, path, method, is_response, service_uuid):
    """Main anonymization function for both requests and responses"""
    endpoint_config = get_endpoint_config(app, path, method, is_response)
    if not endpoint_config:
        return data

    if isinstance(data, list):
        return [
            anonymize_item(item, endpoint_config, service_uuid, path, method, is_response)
            for item in data
        ]
    elif isinstance(data, dict):
        return anonymize_item(data, endpoint_config, service_uuid, path, method, is_response)
    return data




def get_data_category(service_uuid, path, method, field_name, is_response):
    swagger = SwaggerAPI.query.filter_by(service_uuid=service_uuid).first()
    if not swagger:
        return None

    endpoint = Endpoint.query.filter_by(
        swagger_id=swagger.id,
        path = path,
        method=method.upper()
    ).first()
    
    if not endpoint:     
        endpoint = Endpoint.query.filter_by(
        swagger_id=swagger.id,
        path = "/" + path,
        method=method.upper()
    ).first()

    if not endpoint:     
        return None

    field = Field.query.filter_by(
        endpoint_id=endpoint.id,
        name=field_name,
        is_response_field=is_response
    ).first()

    return field.data_category if field else None