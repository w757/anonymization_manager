from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SwaggerAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(255), nullable=False)
    service_uuid = db.Column(db.String(36), unique=True, nullable=False)
    raw_json = db.Column(db.Text, nullable=False)
    endpoints = db.relationship('Endpoint', backref='swagger', lazy=True)

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
    is_response_field = db.Column(db.Boolean, default=False)  # New field
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