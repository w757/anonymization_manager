from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)
api = Api(app)

# Konfiguracja bazy danych SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model użytkownika
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD

    def __repr__(self):
        return f'<User {self.email}>'

# Tworzenie bazy danych
with app.app_context():
    db.create_all()

# Rejestracja użytkownika
class Register(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        address = data.get('address')
        date_of_birth = data.get('date_of_birth')

        # Sprawdzenie, czy użytkownik już istnieje
        if User.query.filter_by(email=email).first():
            return {'message': 'User with this email already exists'}, 400

        # Tworzenie nowego użytkownika
        new_user = User(
            email=email,
            password=password,
            phone_number=phone_number,
            address=address,
            date_of_birth=date_of_birth
        )
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201

# Logowanie użytkownika
class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return {'message': 'Login successful'}, 200
        else:
            return {'message': 'Invalid credentials'}, 401

# Dodawanie zasobów do API
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')

# Konfiguracja Swagger UI
SWAGGER_URL = '/api/docs'  # URL dla Swagger UI
API_URL = '/static/swagger.json'  # URL dla pliku swagger.json

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Authentication API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Tworzenie katalogu `static`, jeśli nie istnieje
if not os.path.exists('static'):
    os.makedirs('static')

# Zapis definicji Swaggera do pliku `static/swagger.json`
swagger_json = {
    "swagger": "2.0",
    "info": {
        "title": "Authentication API",
        "version": "1.0",
        "description": "API for user authentication and registration"
    },
    "paths": {
        "/register": {
            "post": {
                "summary": "Register a new user",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "description": "User's email address"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "User's password"
                                },
                                "phone_number": {
                                    "type": "string",
                                    "description": "User's phone number"
                                },
                                "address": {
                                    "type": "string",
                                    "description": "User's address"
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "format": "date",
                                    "description": "User's date of birth (YYYY-MM-DD)"
                                }
                            },
                            "required": ["email", "password", "phone_number", "address", "date_of_birth"]
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "User registered successfully"
                    },
                    "400": {
                        "description": "User with this email already exists"
                    }
                }
            }
        },
        "/login": {
            "post": {
                "summary": "Login a user",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "description": "User's email address"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "User's password"
                                }
                            },
                            "required": ["email", "password"]
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Login successful"
                    },
                    "401": {
                        "description": "Invalid credentials"
                    }
                }
            }
        }
    }
}

# Zapis do pliku
with open('static/swagger.json', 'w') as f:
    import json
    json.dump(swagger_json, f, indent=4)

if __name__ == '__main__':
    app.run(debug=True)