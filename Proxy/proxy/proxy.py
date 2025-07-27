import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from common.extensions import db
from routes.proxy_routes import proxy_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.register_blueprint(proxy_bp)


if __name__ == '__main__':
   
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/database.db')
    
    with app.app_context():
        db.create_all()  
    app.run(debug=True, host='0.0.0.0', port=5001)