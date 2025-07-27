from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import os
import json

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    pesel = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    salary = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    # Dodana metoda to_dict() do łatwego serializowania obiektu użytkownika
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date,
            'gender': self.gender,
            'pesel': self.pesel,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'street': self.street,
            'postal_code': self.postal_code,
            'city': self.city,
            'country': self.country,
            'password': self.password, # Hasło jest teraz uwzględnione
            'age': self.age,
            'height': self.height,
            'salary': self.salary
        }

with app.app_context():
    db.create_all()

class Register(Resource):
    def post(self):
        data = request.get_json()
        required_fields = [
            'first_name', 'last_name', 'birth_date', 'gender', 'pesel',
            'email', 'phone', 'address', 'street', 'postal_code',
            'city', 'country', 'password', 'age', 'height', 'salary'
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {'message': f'Missing required fields: {", ".join(missing_fields)}'}, 400

        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User with this email already exists'}, 400
        if User.query.filter_by(pesel=data['pesel']).first():
            return {'message': 'User with this PESEL already exists'}, 400

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=data['birth_date'],
            gender=data['gender'],
            pesel=data['pesel'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            street=data['street'],
            postal_code=data['postal_code'],
            city=data['city'],
            country=data['country'],
            password=data['password'],
            age=data['age'],
            height=data['height'],
            salary=data['salary']
        )

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email and password are required'}, 400

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return {'message': 'Login successful'}, 200
        else:
            return {'message': 'Invalid email or password'}, 401

class Users(Resource):
    def get(self):
        users = User.query.all()
        # Użycie nowej metody to_dict() do serializacji wszystkich danych
        users_data = [user.to_dict() for user in users]
        return jsonify(users_data)

class GetUserByID(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            # Użycie nowej metody to_dict() do serializacji wszystkich danych
            user_data = user.to_dict()
            return jsonify(user_data)
        else:
            return {'message': 'User not found'}, 404

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Users, '/users')
api.add_resource(GetUserByID, '/users/<int:user_id>')

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "User Management API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if not os.path.exists('static'):
    os.makedirs('static')

# Zaktualizowany swagger_json, aby odzwierciedlał zwracanie hasła
# Używamy definicji schematu dla User, aby uniknąć duplikowania
swagger_json = {
    "openapi": "3.0.3",
    "info": {
        "title": "User Management API",
        "version": "1.0.0",
        "description": "API for managing user data with comprehensive personal information"
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "birth_date": {"type": "string"},
                    "gender": {"type": "string"},
                    "pesel": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "address": {"type": "string"},
                    "street": {"type": "string"},
                    "postal_code": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                    "password": {"type": "string"}, # Dodano hasło do schematu
                    "age": {"type": "integer"},
                    "height": {"type": "number"},
                    "salary": {"type": "number"}
                },
                "required": [
                    "first_name", "last_name", "birth_date", "gender", "pesel",
                    "email", "phone", "address", "street", "postal_code",
                    "city", "country", "password", "age", "height", "salary"
                ]
            }
        }
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
                                "$ref": "#/components/schemas/User" # Odwołanie do definicji User
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "User registered successfully"},
                    "400": {"description": "Validation error"}
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
                                    "email": {"type": "string"},
                                    "password": {"type": "string"}
                                },
                                "required": ["email", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Login successful"},
                    "400": {"description": "Missing credentials"},
                    "401": {"description": "Invalid credentials"}
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
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/User" # Odwołanie do definicji User
                                    }
                                }
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
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User details returned successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User" # Odwołanie do definicji User
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
        }
    }
}

with open('static/swagger.json', 'w') as f:
    json.dump(swagger_json, f, indent=4)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)