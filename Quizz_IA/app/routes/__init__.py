# Ce fichier peut rester vide ou contenir des imports communs si nécessaire
from flask import Blueprint
from app.routes.auth_routes import auth_routes  # Importer le blueprint
from app.routes.user_routes import user_routes  # Importer le blueprint
from app.routes.summary_routes import utils_routes  # Importer le blueprint
from app.routes.translation_routes import translation_routes
from app.routes.text_to_speech_routes import text_to_speech_routes

def register_blueprints(app):
    # Enregistrer les blueprints dans l'application Flask avec les préfixes appropriés
    app.register_blueprint(auth_routes, url_prefix='/api')
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(utils_routes, url_prefix='/api')
    app.register_blueprint(text_to_speech_routes, url_prefix='/api')
    app.register_blueprint(translation_routes, url_prefix='/api')