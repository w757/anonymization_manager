import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from config import Config
from common.extensions import db, login_manager
from views import register_blueprints

from flask import Flask
from common.models import AnonymizationMethod

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)   # <-- TO DODAJ

    with app.app_context():
        db.create_all()

        if not AnonymizationMethod.query.first():
            from views.utils import seed_default_methods
            seed_default_methods()

    register_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
