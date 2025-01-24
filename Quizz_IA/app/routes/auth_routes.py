import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from app.models import User
from app.utils import compare_image

auth_routes = Blueprint('auth_routes', __name__)

# Dossier temporaire pour sauvegarder les fichiers d'image
TEMP_IMAGE_DIR = "temp_images"

# Assurez-vous que le dossier temporaire existe
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

@auth_routes.route('/authenticate', methods=['POST'])
def authenticate_user():
    """
    Authentifie un utilisateur en utilisant un mot de passe ou une image pour la reconnaissance faciale.
    """
    username = request.form.get('username')  # Nom d'utilisateur fourni
    password = request.form.get('password')  # Mot de passe fourni
    image_file = request.files.get('image_path')  # Image fournie pour la reconnaissance faciale

    # Validation des champs requis
    if not username:
        return jsonify({"error": "Nom d'utilisateur requis."}), 400

    if not password and not image_file:
        return jsonify({"error": "Mot de passe ou image requis pour l'authentification."}), 400

    # Récupérer l'utilisateur dans la base de données
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    # Authentification par mot de passe
    if password:
        if not check_password_hash(user.mdp, password):
            return jsonify({"error": "Mot de passe incorrect."}), 401

    # Authentification par reconnaissance faciale
    if image_file:
        if not user.model_image_path:  # Vérifier si l'utilisateur a une image modèle enregistrée
            return jsonify({"error": "Aucune image modèle n'est enregistrée pour cet utilisateur."}), 404

        try:
            # Sauvegarder l'image temporairement
            temp_image_path = os.path.join(TEMP_IMAGE_DIR, image_file.filename)
            image_file.save(temp_image_path)

            # Comparer l'image fournie avec l'image modèle
            comparison_result = compare_image(temp_image_path, user.model_image_path)

            # Vérifier si une erreur est retournée par compare_image
            if "error" in comparison_result:
                os.remove(temp_image_path)  # Nettoyer le fichier temporaire
                return jsonify({"error": comparison_result["error"]}), 500

            # Vérifier le résultat de la comparaison
            if not comparison_result.get("verified", False):
                os.remove(temp_image_path)  # Nettoyer le fichier temporaire
                return jsonify({"error": "L'image fournie ne correspond pas."}), 401

            # Nettoyer le fichier temporaire
            os.remove(temp_image_path)
        except Exception as e:
            return jsonify({"error": f"Erreur lors de la comparaison d'image : {str(e)}"}), 500

    # Si l'utilisateur est authentifié, générer un token JWT
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Authentification réussie.",
        "access_token": access_token
    }), 200

# Exemple de route protégée par JWT
@auth_routes.route('/protected', methods=['GET'])
@jwt_required()  # Protège la route avec JWT
def protected():
    """
    Exemple de route protégée par JWT.
    L'accès est autorisé uniquement aux utilisateurs authentifiés avec un token JWT.
    """
    user_id = get_jwt_identity()  # Récupérer l'ID de l'utilisateur à partir du token
    return jsonify(message="Accès autorisé !", user_id=user_id), 200
