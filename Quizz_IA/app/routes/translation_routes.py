from flask import Blueprint, request, jsonify
from googletrans import Translator, LANGUAGES

translation_routes = Blueprint('translation_routes', __name__)

def translate_text(text, dest_language):
    """
    Traduit le texte donné vers la langue spécifiée.
    """
    translator = Translator()
    translation = translator.translate(text, dest=dest_language)
    return translation.text

@translation_routes.route('/languages', methods=['GET'])
def get_languages():
    """
    Retourne les langues disponibles pour la traduction.
    """
    return jsonify({"languages": LANGUAGES}), 200

@translation_routes.route('/translate', methods=['POST'])
def translate():
    """
    Traduit un texte envoyé dans une requête POST.
    """
    data = request.get_json()
    text = data.get('text', '')
    dest_language = data.get('dest_language', '')

    if not text or not dest_language:
        return jsonify({"error": "Le texte et la langue cible sont requis."}), 400

    if dest_language not in LANGUAGES:
        return jsonify({"error": "Langue cible non supportée."}), 400

    try:
        translated_text = translate_text(text, dest_language)
        return jsonify({"translated_text": translated_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
