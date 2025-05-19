from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SwaggerAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(200), nullable=False)
    service_uuid = db.Column(db.String(36), unique=True, nullable=False)
    raw_json = db.Column(db.Text, nullable=False)
    encryption_key = db.Column(db.String(64), nullable=False)
    endpoints = db.relationship('Endpoint', backref='swagger', lazy=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('swagger_apis', lazy=True))




class Endpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swagger_id = db.Column(db.Integer, db.ForeignKey('swagger_api.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    fields = db.relationship('Field', backref='endpoint', lazy=True)

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoint.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    data_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_response_field = db.Column(db.Boolean, default=False)
    data_category = db.Column(db.String(50), nullable=True)  # Nowe pole dla kategorii danych
    anonymization = db.relationship('FieldAnonymization', backref='field', uselist=False)
    
class AnonymizationMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)

class FieldAnonymization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    anonymization_method_id = db.Column(db.Integer, db.ForeignKey('anonymization_method.id'), nullable=True)
    anonymization_method = db.relationship('AnonymizationMethod', backref='field_anonymizations')