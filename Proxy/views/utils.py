from models import Field, FieldAnonymization, Endpoint
from extensions import db

def extract_schema_properties(schema):
    if not schema:
        return {}
    if 'allOf' in schema:
        combined_props = {}
        for item in schema['allOf']:
            combined_props.update(extract_schema_properties(item))
        return combined_props
    if schema.get('type') == 'array' and 'items' in schema:
        return extract_schema_properties(schema['items'])
    return schema.get('properties', {})

def process_schema_fields(endpoint_id, properties, is_response=False):
    for field_name, field_info in properties.items():
        field = Field(
            endpoint_id=endpoint_id,
            name=field_name,
            data_type=field_info.get("type", "string"),
            description=field_info.get("description", ""),
            is_response_field=is_response
        )
        db.session.add(field)
        db.session.commit()
        db.session.add(FieldAnonymization(field_id=field.id))

def parse_openapi(swagger, parsed_data):
    for path, methods in parsed_data.get("paths", {}).items():
        for method, details in methods.items():
            endpoint = Endpoint(swagger_id=swagger.id, path=path, method=method.upper())
            db.session.add(endpoint)
            db.session.commit()

            for param in details.get("parameters", []):
                param_name = param.get("name")
                param_type = param.get("schema", {}).get("type", "object")
                field = Field(endpoint_id=endpoint.id, name=param_name, data_type=param_type, is_response_field=False)
                db.session.add(field)

            request_schema = details.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if request_schema:
                props = extract_schema_properties(request_schema)
                process_schema_fields(endpoint.id, props, is_response=False)

            for response in details.get("responses", {}).values():
                response_schema = response.get("schema")
                if not response_schema:
                    content = response.get("content", {}).get("application/json", {})
                    example = content.get("example")
                    if isinstance(example, list) and example:
                        props = {k: {"type": type(v).__name__} for k, v in example[0].items()}
                        process_schema_fields(endpoint.id, props, is_response=True)
                    elif isinstance(example, dict):
                        props = {k: {"type": type(v).__name__} for k, v in example.items()}
                        process_schema_fields(endpoint.id, props, is_response=True)
                else:
                    props = extract_schema_properties(response_schema)
                    process_schema_fields(endpoint.id, props, is_response=True)

    db.session.commit()

def seed_default_methods():
    from models import AnonymizationMethod
    default_methods = [
        ("Noise", "Anonymization"),
        ("Generalization", "Anonymization"),
        ("Masking", "Anonymization"),
        ("Fabrication", "Anonymization"),
        ("Hashing", "Pseudonymization"),
        ("Encryption", "Pseudonymization")
    ]
    for method, category in default_methods:
        db.session.add(AnonymizationMethod(name=method, category=category))
    db.session.commit()
