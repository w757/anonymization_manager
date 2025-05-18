

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

DATA_CATEGORIES = [
    ('', '-- Select data category --'),
    ('first_name', 'First name'),
    ('last_name', 'Last name'),
    ('birth_date', 'Birth date'),
    ('gender', 'Gender'),
    ('pesel', 'PESEL'),
    ('email', 'Email'),
    ('phone', 'Phone number'),
    ('address', 'Address'),
    ('street', 'Street'),
    ('postal_code', 'Postal code'),
    ('city', 'City'),
    ('country', 'Country'),
    ('password', 'Password'),
    ('age', 'Age'),
    ('height', 'Height'),
    ('salary', 'Salary')
]

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

    data_category = SelectField(
        "Data Category",
        choices=DATA_CATEGORIES,
        validators=[DataRequired()]
    )

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wypełnij kategorie
        self.category.choices = [
            ("Anonymization", "Anonymization"), 
            ("Pseudonymization", "Pseudonymization")
        ]

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Wypełnij kategorie
    #     self.category.choices = [
    #         ("Anonymization", "Anonymization"), 
    #         ("pseudoanonimizacja", "Pseudoanonimizacja")
    #     ]
