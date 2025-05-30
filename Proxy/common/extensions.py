from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'  # Nazwa endpointu logowania
login_manager.login_message = 'Musisz się zalogować, aby uzyskać dostęp do tej strony.'
login_manager.login_message_category = 'warning'
