from .proxy_routes import proxy_bp

def register_routes(app):
    app.register_blueprint(proxy_bp)
