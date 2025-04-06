

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, URL
from models import AnonymizationMethod, db
import uuid

class SwaggerForm(FlaskForm):
    """Form to upload Swagger JSON."""
    api_url = StringField("API URL", validators=[DataRequired(), URL(message="Please enter a valid URL.")])
    swagger_json = TextAreaField("Swagger JSON", validators=[DataRequired()])
    service_uuid = HiddenField("Service UUID", default=lambda: str(uuid.uuid4()))
    submit = SubmitField("Upload")

class AnonymizationForm(FlaskForm):
    """Form to select an anonymization method for a specific field."""
    category = SelectField(
        "Category",
        choices=[],  # Początkowo puste, będzie wypełniane dynamicznie
        validators=[DataRequired()]
    )

    anonymization_method = SelectField(
        "Anonymization Method",
        choices=[],  # Początkowo puste
        validators=[DataRequired()]
    )

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wypełnij kategorie
        self.category.choices = [
            ("anonimizacja", "Anonimizacja"), 
            ("pseudoanonimizacja", "Pseudoanonimizacja")
        ]
