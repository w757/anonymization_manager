import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, SwaggerAPI, Endpoint, Field, AnonymizationMethod, FieldAnonymization  # Added FieldAnonymization
from forms import SwaggerForm, AnonymizationForm
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db.init_app(app)

def init_db():
    """Ensure the database is created properly."""
    with app.app_context():
        if not os.path.exists("database.db"):
            db.create_all()
            print("✅ Database created successfully!")
        
        # ✅ Ensure anonymization methods exist
        if not AnonymizationMethod.query.first():
            default_methods = ["Masking", "Encryption", "Tokenization", "None"]
            for method in default_methods:
                db.session.add(AnonymizationMethod(name=method))
            db.session.commit()
            print("✅ Default anonymization methods inserted!")

init_db()



@app.route("/", methods=["GET", "POST"])
def index():
    form = SwaggerForm()
    
    if form.validate_on_submit():
        api_url = form.api_url.data
        swagger_json = form.swagger_json.data

        try:
            parsed_data = json.loads(swagger_json)
        except json.JSONDecodeError:
            flash("Invalid JSON format", "danger")
            return redirect(url_for("index"))

        # Check if Swagger already exists
        existing_swagger = SwaggerAPI.query.filter_by(api_url=api_url).first()  # Updated field name
        if existing_swagger:
            flash("Swagger API with this URL already exists!", "warning")
            return redirect(url_for("index"))

        # Store Swagger JSON in database
        swagger = SwaggerAPI(api_url=api_url, raw_json=swagger_json)  # Updated field name
        db.session.add(swagger)
        db.session.commit()

        # Extract endpoints and store them in the database
        for path, methods in parsed_data.get("paths", {}).items():
            for method, details in methods.items():
                endpoint = Endpoint(swagger_id=swagger.id, path=path, method=method.upper())
                db.session.add(endpoint)
                db.session.commit()

                # Store fields separately
                for param in details.get("parameters", []):
                    if param.get("in") == "body":
                        for field_name, field_info in param.get("schema", {}).get("properties", {}).items():
                            field = Field(
                                endpoint_id=endpoint.id,
                                name=field_name,
                                data_type=field_info.get("type", "string"),
                                description=field_info.get("description", "")
                            )
                            db.session.add(field)
                            db.session.commit()

                            # Create a FieldAnonymization record for the field
                            field_anonymization = FieldAnonymization(
                                field_id=field.id,
                                anonymization_method_id=None  # Default to no anonymization method
                            )
                            db.session.add(field_anonymization)

        db.session.commit()
        flash("Swagger uploaded successfully!", "success")
        return redirect(url_for("index"))

    swaggers = SwaggerAPI.query.all()
    return render_template("index.html", form=form, swaggers=swaggers)



@app.route("/swagger/<int:id>")
def swagger_details(id):
    swagger = SwaggerAPI.query.get_or_404(id)
    endpoints = Endpoint.query.filter_by(swagger_id=id).all()
    return render_template("swagger_details.html", swagger=swagger, endpoints=endpoints)

@app.route("/edit_anonymization/<int:field_id>", methods=["GET", "POST"])
def edit_anonymization(field_id):
    field = Field.query.get_or_404(field_id)  # Get the specific field
    form = AnonymizationForm(obj=field)

    if form.validate_on_submit():
        # Get the selected anonymization method ID
        anonymization_method_id = form.anonymization_method.data

        # Check if a FieldAnonymization record already exists for this field
        if field.anonymization:
            # Update existing anonymization method
            field.anonymization.anonymization_method_id = anonymization_method_id
        else:
            # Create a new FieldAnonymization record
            field_anonymization = FieldAnonymization(
                field_id=field.id,
                anonymization_method_id=anonymization_method_id
            )
            db.session.add(field_anonymization)

        db.session.commit()
        flash("Anonymization method updated successfully!", "success")

        # Redirect to the swagger_details page and scroll to the specific endpoint
        return redirect(url_for("swagger_details", id=field.endpoint.swagger_id, _anchor=f"endpoint-{field.endpoint.id}"))

    return render_template("edit_anonymization.html", form=form, field=field)



@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    # Define error details based on the error code
    error_code = getattr(error, 'code', 500)  # Default to 500 if no code is found
    error_messages = {
        400: ("Bad Request", "The request was invalid or cannot be served."),
        404: ("Not Found", "The page you're looking for doesn't exist."),
        500: ("Internal Server Error", "Something went wrong on our end. Please try again later."),
    }
    error_message, error_description = error_messages.get(error_code, ("Error", "An unexpected error occurred."))

    # Render the error page with the error details
    return render_template(
        'error_page.html',
        error_code=error_code,
        error_message=error_message,
        error_description=error_description
    ), error_code


if __name__ == "__main__":
    app.run(debug=True)