from flask import Blueprint, request, jsonify
from app.utils import summarize_text_simple
from chardet import detect
import PyPDF2
import docx

utils_routes = Blueprint('utils_routes', __name__)

@utils_routes.route('/summarize', methods=['POST'])
def summarize_text():
    """
    Résume un texte ou un fichier envoyé dans une requête POST.
    """
    try:
        # Récupérer le ratio depuis la requête (avec une valeur par défaut de 0.2)
        ratio = float(request.form.get('ratio', 0.2))

        # Vérifier que le ratio est dans une plage valide (0.1 à 1)
        if not (0.1 <= ratio <= 1):
            return jsonify({"error": "Le ratio doit être compris entre 0.1 et 1."}), 400

    except ValueError:
        return jsonify({"error": "Le ratio doit être un nombre valide."}), 400

    # Résumer un texte
    if 'text' in request.form:
        text = request.form.get('text', '').strip()

        if not text:
            return jsonify({"error": "Le texte est requis pour le résumé."}), 400

        summary = summarize_text_simple(text, ratio)
        return jsonify({"summary": summary})

    # Résumer un fichier
    elif 'file' in request.files:
        uploaded_file = request.files['file']

        # Vérifier que le fichier n'est pas vide
        if uploaded_file.filename == '':
            return jsonify({"error": "Un fichier valide est requis pour le résumé."}), 400

        try:
            # Lire le contenu du fichier
            file_content = uploaded_file.read()

            # Détecter l'encodage avec chardet
            detected_encoding = detect(file_content)['encoding']

            # Si l'encodage est détecté comme None, on utilise un encodage par défaut
            if detected_encoding is None:
                detected_encoding = 'ISO-8859-1'  # Vous pouvez essayer d'autres encodages si nécessaire

            # Essayer de décoder le contenu avec l'encodage détecté
            file_content = file_content.decode(detected_encoding)

            # Si c'est un fichier PDF, nous devons extraire le texte
            if uploaded_file.filename.lower().endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                file_content = ""
                for page in pdf_reader.pages:
                    file_content += page.extract_text()

            # Si c'est un fichier Word (docx), extraire le texte
            elif uploaded_file.filename.lower().endswith('.docx'):
                doc = docx.Document(uploaded_file)
                file_content = ""
                for para in doc.paragraphs:
                    file_content += para.text + '\n'

        except Exception as e:
            return jsonify({"error": f"Erreur lors de la lecture du fichier : {str(e)}"}), 400

        # Vérifier que le fichier contient du texte
        if not file_content.strip():
            return jsonify({"error": "Le fichier ne contient aucun texte pour le résumé."}), 400

        summary = summarize_text_simple(file_content, ratio)
        return jsonify({"summary": summary})

    else:
        # Aucun texte ou fichier fourni
        return jsonify({"error": "Veuillez fournir un texte ou un fichier pour le résumé."}), 400
