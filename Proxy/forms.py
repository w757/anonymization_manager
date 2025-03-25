# from flask_wtf import FlaskForm
# from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
# from wtforms.validators import DataRequired, URL
# from models import AnonymizationMethod, db
# import uuid

# class SwaggerForm(FlaskForm):
#     """Form to upload Swagger JSON."""
#     api_url = StringField("API URL", validators=[DataRequired(), URL(message="Please enter a valid URL.")])
#     swagger_json = TextAreaField("Swagger JSON", validators=[DataRequired()])
#     service_uuid = HiddenField("Service UUID", default=lambda: str(uuid.uuid4()))
#     submit = SubmitField("Upload")

# class AnonymizationMethodForm(FlaskForm):
#     """Form to manage anonymization methods."""
#     name = StringField("Method Name", validators=[DataRequired()])
#     description = TextAreaField("Description")
#     submit = SubmitField("Save")

# class FieldAnonymizationForm(FlaskForm):
#     """Form to assign anonymization method to field."""
#     anonymization_method = SelectField("Anonymization Method", coerce=int, validators=[DataRequired()])
#     submit = SubmitField("Save")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.anonymization_method.choices = [(m.id, m.name) for m in AnonymizationMethod.query.all()]

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
    anonymization_method = SelectField("Anonymization Method", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with db.session.no_autoflush:
            self.anonymization_method.choices = [(m.id, m.name) for m in AnonymizationMethod.query.all()]