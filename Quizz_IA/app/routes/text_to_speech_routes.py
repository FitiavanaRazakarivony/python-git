from flask import Blueprint, request, jsonify
from app.utils import text_to_speech, pause_speech, resume_speech, stop_speech
text_to_speech_routes = Blueprint('text_to_speech_routes', __name__)

@text_to_speech_routes.route('/text-to-speech', methods=['POST'])
def text_to_speech_route():
    """
    Accepte un texte et renvoie une réponse de succès ou d'erreur.
    Effectue la conversion en parole.
    """
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "Le texte est requis pour la conversion."}), 400

    try:
        text_to_speech(text)
        return jsonify({"message": "Conversion en parole réussie."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@text_to_speech_routes.route('/pause', methods=['POST'])
def pause_route():
    try:
        message = pause_speech()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@text_to_speech_routes.route('/resume', methods=['POST'])
def resume_route():
    try:
        message = resume_speech()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@text_to_speech_routes.route('/stop', methods=['POST'])
def stop_route():
    try:
        stop_speech()
        return jsonify({"message": "Speech stopped."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500