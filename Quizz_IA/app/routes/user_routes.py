from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
from app.utils import save_uploaded_file

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/register', methods=['POST'])
def register_user():
    try:
        username = request.form.get('username')  # Correspond à `signupData.username` côté Angular
        email = request.form.get('email')
        password = request.form.get('password')
        model_image = request.files.get('image_path')  # Fichier envoyé par le composant `app-camera`

        if not all([username, email, password, model_image]):
            return jsonify({"error": "Tous les champs sont requis (nom, email, mot de passe, image)."}), 400

        # Hachage du mot de passe
        hashed_password = generate_password_hash(password)

        # Sauvegarde de l'image physique
        image_path = save_uploaded_file('uploads', model_image)

        # Enregistrement dans la base de données
        new_user = User(username=username, email=email, mdp=hashed_password, model_image_path=image_path)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": f"Utilisateur '{username}' inscrit avec succès."}), 201

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'inscription : {str(e)}"}), 500

