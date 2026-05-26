from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Importar y registrar las rutas (Blueprints)
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app