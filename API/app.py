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

# Pobieranie użytkowników
class Users(Resource):
    def get(self):
        users = User.query.all()
        users_data = [
            {
                'id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
                'address': user.address,
                'date_of_birth': user.date_of_birth
            } for user in users
        ]
        return jsonify(users_data)

# Pobieranie użytkownika po ID
class GetUserByID(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            user_data = {
                'id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
                'address': user.address,
                'date_of_birth': user.date_of_birth
            }
            return jsonify(user_data)
        else:
            return {'message': 'User not found'}, 404

# Pobieranie użytkowników po adresie
class GetUsersByAddress(Resource):
    def get(self):
        address = request.args.get('address')
        if not address:
            return {'message': 'Address parameter is required'}, 400
        
        users = User.query.filter(User.address.contains(address)).all()
        users_data = [
            {
                'id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
                'address': user.address,
                'date_of_birth': user.date_of_birth
            } for user in users
        ]
        return jsonify(users_data)

# Dodawanie zasobów do API
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Users, '/users')
api.add_resource(GetUserByID, '/users/<int:user_id>')
api.add_resource(GetUsersByAddress, '/users/by_address')

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
    "openapi": "3.0.3",
    "info": {
        "title": "Authentication API",
        "version": "1.0.0",
        "description": "API for user authentication and registration"
    },
    "paths": {
        "/register": {
            "post": {
                "summary": "Register a new user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email", "example": "user@example.com"},
                                    "password": {"type": "string", "example": "securePassword123"},
                                    "phone_number": {"type": "string", "example": "+48123456789"},
                                    "address": {"type": "string", "example": "ul. Przykładowa 123, Warszawa"},
                                    "date_of_birth": {"type": "string", "format": "date", "example": "1990-01-15"}
                                },
                                "required": ["email", "password", "phone_number", "address", "date_of_birth"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User registered successfully",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "User registered successfully"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "User with this email already exists",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "User with this email already exists"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/login": {
            "post": {
                "summary": "Login a user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email", "example": "user@example.com"},
                                    "password": {"type": "string", "example": "securePassword123"}
                                },
                                "required": ["email", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "Login successful"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Invalid credentials",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "Invalid credentials"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/users": {
            "get": {
                "summary": "Get list of users",
                "responses": {
                    "200": {
                        "description": "List of users returned successfully",
                        "content": {
                            "application/json": {
                                "example": [
                                    {
                                        "id": 1,
                                        "email": "user1@example.com",
                                        "phone_number": "+48123456789",
                                        "address": "ul. Przykładowa 123, Warszawa",
                                        "date_of_birth": "1990-01-15"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        },
        "/users/{user_id}": {
            "get": {
                "summary": "Get user by ID",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        },
                        "description": "ID of the user to retrieve"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User details returned successfully",
                        "content": {
                            "application/json": {
                                "example": {
                                    "id": 1,
                                    "email": "user1@example.com",
                                    "phone_number": "+48123456789",
                                    "address": "ul. Przykładowa 123, Warszawa",
                                    "date_of_birth": "1990-01-15"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "User not found"
                                }
                            }
                        }
                    }
                }
            }
        },
        "/users/by_address": {
            "get": {
                "summary": "Get users by address",
                "parameters": [
                    {
                        "name": "address",
                        "in": "query",
                        "required": True,
                        "schema": {
                            "type": "string"
                        },
                        "description": "Address to search for (can be partial)"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of users matching the address",
                        "content": {
                            "application/json": {
                                "example": [
                                    {
                                        "id": 1,
                                        "email": "user1@example.com",
                                        "phone_number": "+48123456789",
                                        "address": "ul. Przykładowa 123, Warszawa",
                                        "date_of_birth": "1990-01-15"
                                    }
                                ]
                            }
                        }
                    },
                    "400": {
                        "description": "Address parameter is required",
                        "content": {
                            "application/json": {
                                "example": {
                                    "message": "Address parameter is required"
                                }
                            }
                        }
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
    app.run(port=8080)