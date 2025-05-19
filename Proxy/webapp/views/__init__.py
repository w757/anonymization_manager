from .auth_routes import auth_bp
from .swagger_routes import swagger_bp
from .anonymization_routes import anonymization_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(swagger_bp)
    app.register_blueprint(anonymization_bp)
