import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, SwaggerAPI, Endpoint, Field, AnonymizationMethod, FieldAnonymization
from forms import SwaggerForm, AnonymizationForm
import json



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
                    ("Masking", "anonimizacja"),
                    ("Encryption", "anonimizacja"),
                    ("Tokenization", "pseudoanonimizacja"),
                    ("None", "anonimizacja")
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
                raw_json=form.swagger_json.data
            )
            db.session.add(swagger)
            db.session.commit()

            if "paths" in parsed_data:
                for path, methods in parsed_data["paths"].items():
                    for method, details in methods.items():
                        endpoint = Endpoint(
                            swagger_id=swagger.id,
                            path=path,
                            method=method.upper()
                        )
                        db.session.add(endpoint)
                        db.session.commit()

                        # Process request parameters
                        if "parameters" in details:
                            for param in details["parameters"]:
                                if param.get("in") == "body" and "schema" in param:
                                    process_schema_fields(
                                        endpoint.id,
                                        param["schema"].get("properties", {}),
                                        is_response=False
                                    )

                        # Process response schemas
                        if "responses" in details:
                            for response_code, response in details["responses"].items():
                                if "schema" in response:
                                    if response["schema"].get("type") == "object":
                                        process_schema_fields(
                                            endpoint.id,
                                            response["schema"].get("properties", {}),
                                            is_response=True
                                        )
                                    elif response["schema"].get("type") == "array":
                                        if "items" in response["schema"] and "properties" in response["schema"]["items"]:
                                            process_schema_fields(
                                                endpoint.id,
                                                response["schema"]["items"].get("properties", {}),
                                                is_response=True
                                            )

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
    form = AnonymizationForm()

    # Dla żądania GET - wczytaj istniejące wartości
    if request.method == 'GET':
        if field.anonymization and field.anonymization.anonymization_method:
            form.category.data = field.anonymization.anonymization_method.category
            # Nie ustawiamy metody tutaj, bo zostanie załadowana przez JavaScript

    # Dla żądania POST - zapisz zmiany
    if request.method == 'POST':
        # Pobierz ID metody z formularza
        method_id = request.form.get('anonymization_method')
        
        if not method_id:
            flash("Please select an anonymization method", "danger")
            return redirect(url_for('edit_anonymization', field_id=field.id))

        # Sprawdź czy metoda istnieje
        method = AnonymizationMethod.query.get(method_id)
        if not method:
            flash("Invalid method selected", "danger")
            return redirect(url_for('edit_anonymization', field_id=field.id))

        # Upewnij się, że istnieje rekord FieldAnonymization
        if not field.anonymization:
            field.anonymization = FieldAnonymization(field_id=field.id)
            db.session.add(field.anonymization)

        # Aktualizuj metodę
        field.anonymization.anonymization_method_id = method.id
        
        try:
            db.session.commit()
            flash("Anonymization method updated successfully!", "success")
            return redirect(url_for(
                "swagger_details",
                id=field.endpoint.swagger_id,
                _anchor=f"endpoint-{field.endpoint.id}"
            ))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving changes: {str(e)}", "danger")

    return render_template(
        "edit_anonymization.html",
        form=form,
        field=field,
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