

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, SwaggerAPI, Endpoint, Field, AnonymizationMethod, FieldAnonymization
from forms import SwaggerForm, AnonymizationForm
import json
#from data_identifier import analyze_field
import secrets



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)

def init_db():
    with app.app_context():
        if not os.path.exists("database.db"):
            db.create_all()
            if not AnonymizationMethod.query.first():
                default_methods = [
                    ("Generalization", "Anonymization"),
                    ("Suppression", "Anonymization"),
                    ("Aggregation", "Anonymization"),
                    ("Masking", "Anonymization"),
                    ("Hashing", "Pseudonymization"),
                    ("Encryption", "Pseudonymization")
                ]
                for method, category in default_methods:
                    anonymization_method = AnonymizationMethod(
                        name=method,
                        category=category
                    )
                    db.session.add(anonymization_method)
                db.session.commit()

init_db()

def process_schema_fields(endpoint_id, properties, is_response=False):
    """Process fields from both request and response schemas"""
    for field_name, field_info in properties.items():
        field = Field(
            endpoint_id=endpoint_id,
            name=field_name,
            data_type=field_info.get("type", "string"),
            description=field_info.get("description", ""),
            is_response_field=is_response  # New flag to distinguish response fields
        )
        db.session.add(field)
        db.session.commit()
        
        field_anonymization = FieldAnonymization(field_id=field.id)
        db.session.add(field_anonymization)

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



def parse_openapi(swagger, parsed_data):
    for path, methods in parsed_data.get("paths", {}).items():
        for method, details in methods.items():
            endpoint = Endpoint(
                swagger_id=swagger.id,
                path=path,
                method=method.upper()
            )
            db.session.add(endpoint)
            db.session.commit()

            # ✅ 1. Parametry (query, path, header, cookie)
            for param in details.get("parameters", []):
                param_name = param.get("name")
                param_schema = param.get("schema", {})
                param_type = param_schema.get("type", "object")

                field = Field(
                    endpoint_id=endpoint.id,
                    name=param_name,
                    data_type=param_type,
                    is_response_field=False
                )
                db.session.add(field)

            # ✅ 2. requestBody (OpenAPI 3 only)
            request_schema = details.get("requestBody", {}) \
                .get("content", {}) \
                .get("application/json", {}) \
                .get("schema")

            if request_schema:
                props = extract_schema_properties(request_schema)
                process_schema_fields(endpoint.id, props, is_response=False)

            # ✅ 3. Responses
            for response in details.get("responses", {}).values():
                response_schema = response.get("schema")  # OAS2
                if not response_schema:
                    content = response.get("content", {}).get("application/json", {})
                    example = content.get("example")

                    if example:
                        # Jeśli example to lista (np. GET /users)
                        if isinstance(example, list) and len(example) > 0:
                            first = example[0]
                            if isinstance(first, dict):
                                props = {k: {"type": type(v).__name__} for k, v in first.items()}
                                process_schema_fields(endpoint.id, props, is_response=True)
                        # Jeśli example to pojedynczy obiekt (np. GET /users/{id})
                        elif isinstance(example, dict):
                            props = {k: {"type": type(v).__name__} for k, v in example.items()}
                            process_schema_fields(endpoint.id, props, is_response=True)
                else:
                    props = extract_schema_properties(response_schema)
                    process_schema_fields(endpoint.id, props, is_response=True)


    db.session.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    form = SwaggerForm()
    if form.validate_on_submit():
        try:
            parsed_data = json.loads(form.swagger_json.data)
            if SwaggerAPI.query.filter_by(api_url=form.api_url.data).first():
                flash("API URL already exists!", "warning")
                return redirect(url_for("index"))

            swagger = SwaggerAPI(
                api_url=form.api_url.data,
                service_uuid=form.service_uuid.data,
                raw_json=form.swagger_json.data,
                encryption_key=secrets.token_hex(32)  # Dodaj klucz szyfrowania
            )
            db.session.add(swagger)
            db.session.commit()

            parse_openapi(swagger, parsed_data)
            db.session.commit()

            flash(f"Swagger uploaded! Service UUID: {form.service_uuid.data}", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("index.html", form=form, swaggers=SwaggerAPI.query.all())




@app.route("/swagger/<int:id>")
def swagger_details(id):
    swagger = SwaggerAPI.query.get_or_404(id)
    endpoints = Endpoint.query.filter_by(swagger_id=id).all()
    return render_template(
        "swagger_details.html",
        swagger=swagger,
        endpoints=endpoints
    )


@app.route('/get_anonymization_methods', methods=['POST'])
def get_anonymization_methods():
    data = request.get_json()
    methods = AnonymizationMethod.query.filter_by(category=data['category']).all()
    return jsonify([{'id': m.id, 'name': m.name} for m in methods])



@app.route("/edit_anonymization/<int:field_id>", methods=["GET", "POST"])
def edit_anonymization(field_id):
    field = Field.query.get_or_404(field_id)
    endpoint = field.endpoint
    swagger = endpoint.swagger
    
    # Pobierz przykładową wartość z Swaggera
    example_value = None
    try:
        swagger_data = json.loads(swagger.raw_json)
        path_info = swagger_data['paths'].get(endpoint.path, {}).get(endpoint.method.lower(), {})
        
        if field.is_response_field:
            # Dla pól w odpowiedzi
            for response in path_info.get('responses', {}).values():
                content = response.get('content', {}).get('application/json', {})
                if 'example' in content:
                    if isinstance(content['example'], list) and content['example']:
                        example_value = content['example'][0].get(field.name)
                    elif isinstance(content['example'], dict):
                        example_value = content['example'].get(field.name)
        else:
            # Dla pól w żądaniu
            request_body = path_info.get('requestBody', {}).get('content', {}).get('application/json', {})
            if 'schema' in request_body and 'properties' in request_body['schema']:
                example_value = request_body['schema']['properties'].get(field.name, {}).get('example')
   
        # if example_value:
        #     data_analysis = analyze_field(field.name, example_value)
            
    except Exception as e:
        print(f"Error parsing Swagger JSON: {e}")

    form = AnonymizationForm()

  # Dla żądania GET - wczytaj istniejące wartości
    if request.method == 'GET':
        if field.anonymization and field.anonymization.anonymization_method:
            form.category.data = field.anonymization.anonymization_method.category
        form.data_category.data = field.data_category  # Wczytaj istniejącą kategorię danych

    # Dla żądania POST - zapisz zmiany
    if request.method == 'POST':
        method_id = request.form.get('anonymization_method')
        
        if not method_id:
            flash("Please select an anonymization method", "danger")
            return redirect(url_for('edit_anonymization', field_id=field.id))

        method = AnonymizationMethod.query.get(method_id)
        if not method:
            flash("Invalid method selected", "danger")
            return redirect(url_for('edit_anonymization', field_id=field.id))

        if not field.anonymization:
            field.anonymization = FieldAnonymization(field_id=field.id)
            db.session.add(field.anonymization)

        field.anonymization.anonymization_method_id = method.id
        field.data_category = form.data_category.data  # Zapisz kategorię danych
        
        try:
            db.session.commit()
            flash("Anonymization method updated successfully!", "success")
            return redirect(url_for(
                "swagger_details",
                id=endpoint.swagger_id,
                _anchor=f"endpoint-{endpoint.id}"
            ))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving changes: {str(e)}", "danger")

    # Reszta kodu pozostaje bez zmian
    return render_template(
        "edit_anonymization.html",
        form=form,
        field=field,
        endpoint=endpoint,
        swagger=swagger,
        example_value=example_value,
        current_method=field.anonymization.anonymization_method if field.anonymization else None
    )

@app.route("/delete_swagger/<int:id>", methods=["POST"])
def delete_swagger(id):
    swagger = SwaggerAPI.query.get_or_404(id)
    
    # First delete all related records
    endpoints = Endpoint.query.filter_by(swagger_id=id).all()
    for endpoint in endpoints:
        # Delete all fields and their anonymizations for this endpoint
        fields = Field.query.filter_by(endpoint_id=endpoint.id).all()
        for field in fields:
            FieldAnonymization.query.filter_by(field_id=field.id).delete()
            db.session.delete(field)
        
        # Delete the endpoint itself
        db.session.delete(endpoint)
    
    # Now delete the swagger
    db.session.delete(swagger)
    db.session.commit()
    
    flash("Swagger configuration deleted successfully!", "success")
    return redirect(url_for("index"))

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    error_code = getattr(error, 'code', 500)
    error_messages = {
        400: ("Bad Request", "The request was invalid or cannot be served."),
        404: ("Not Found", "The page you're looking for doesn't exist."),
        500: ("Internal Server Error", "Something went wrong on our end."),
    }
    error_message, error_description = error_messages.get(
        error_code,
        ("Error", "An unexpected error occurred.")
    )
    return render_template(
        'error_page.html',
        error_code=error_code,
        error_message=error_message,
        error_description=error_description
    ), error_code

if __name__ == "__main__":
    app.run(debug=True)
