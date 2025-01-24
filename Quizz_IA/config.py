from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

class Config:
    """
    Configuration générale de l'application.
    """
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:@localhost/facial_auth')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration du dossier de téléchargement
    UPLOAD_FOLDER = 'uploads'

    # Clé secrète utilisée pour signer les tokens JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre_clé_secrète')

    # Clé secrète pour JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'votre_clé_jwt_secrète')  # Clé secrète pour les tokens JWT
