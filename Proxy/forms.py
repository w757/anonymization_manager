
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL
from models import AnonymizationMethod, db

#db = SQLAlchemy()

class SwaggerForm(FlaskForm):
    """Form to upload Swagger JSON."""
    api_url = StringField("API URL", validators=[DataRequired(), URL(message="Please enter a valid URL.")])  # Updated field with URL validator
    swagger_json = TextAreaField("Swagger JSON", validators=[DataRequired()])
    submit = SubmitField("Upload")

class FieldAnonymizationForm(FlaskForm):
    """Form to select an anonymization method for a specific field."""
    anonymization_method = SelectField("Anonymization Method", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with db.session.no_autoflush:  # Prevents issues with app context
            self.anonymization_method.choices = [(m.id, m.name) for m in AnonymizationMethod.query.all()]


class AnonymizationForm(FlaskForm):
    anonymization_method = SelectField("Anonymization Method", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with db.session.no_autoflush:
            self.anonymization_method.choices = [(m.id, m.name) for m in AnonymizationMethod.query.all()]