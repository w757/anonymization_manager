from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, URL, Optional, EqualTo, Length
from common.models import AnonymizationMethod, db
import uuid

class SwaggerForm(FlaskForm):
    """Form to upload Swagger JSON."""
    api_url = StringField("API URL", validators=[DataRequired(), URL(message="Please enter a valid URL.")])
    swagger_json = TextAreaField("Swagger JSON", validators=[DataRequired()])
    service_uuid = HiddenField("Service UUID", default=lambda: str(uuid.uuid4()))
    submit = SubmitField("Upload")


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AnonymizationForm(FlaskForm):
    """Form to select an anonymization method for a specific field."""
    category = SelectField(
        "Category",
        choices=[], 
        validators=[DataRequired()]
    )

    anonymization_method = SelectField(
        "Anonymization Method",
        choices=[],  
        validators=[DataRequired()]
    )

    data_category = SelectField(
        "Data Category",
        choices=[],
        validators=[Optional()]
    )

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [
            ("Anonymization", "Anonymization"), 
            ("Pseudonymization", "Pseudonymization")
        ]

