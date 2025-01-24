import os
from transformers import pipeline
from gtts import gTTS
from langdetect import detect
from deepface import DeepFace
from werkzeug.utils import secure_filename
from langdetect import detect
import pyttsx3
import threading


engine = pyttsx3.init()
lock = threading.Lock()  # Verrou pour empêcher plusieurs threads d'appeler runAndWait()

# Comparaison des images avec vérifications des chemins
def compare_image(image_file, image_model):
    try:
        # Construire le chemin complet de l'image modèle
        model_image_path = os.path.join('uploads', image_model)  # Assurez-vous que 'uploads' est le bon répertoire

        # Vérifier si le fichier image modèle existe
        if not os.path.exists(model_image_path):
            raise FileNotFoundError(f"Le fichier modèle '{model_image_path}' est introuvable.")

        # Vérifier si le fichier image fourni existe
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Le fichier temporaire '{image_file}' est introuvable.")

        # Effectuer la comparaison avec DeepFace
        result = DeepFace.verify(image_file, model_image_path, enforce_detection=False)

        # Extraire les informations pertinentes
        if result.get("verified", False):
            print(f"Les deux images correspondent avec une distance de {result['distance']:.4f}.")
        else:
            print(f"Les deux images ne correspondent pas. Distance : {result['distance']:.4f}.")

        return result

    except FileNotFoundError as fnf_error:
        print(f"Erreur de fichier : {fnf_error}")
        return {"error": str(fnf_error)}

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return {"error": str(e)}

# authentification
def save_temp_image(image_file, temp_folder='temp_images'):
    """
    Sauvegarde temporairement l'image dans un dossier et retourne son chemin.
    """
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    filename = secure_filename(image_file.filename)
    file_path = os.path.join(temp_folder, filename)
    image_file.save(file_path)

    return file_path

# fin authentification
def save_uploaded_file(upload_folder, file):
    """
    Sauvegarde un fichier téléchargé et renvoie son nom de fichier sécurisé.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    return filename

def summarize_text_simple(text, ratio):
    """
    Résume un texte donné en fonction du ratio.
    """
    # Diviser le texte en phrases, en prenant soin de ne pas laisser de 'vide' à la fin
    sentences = [sentence.strip() for sentence in text.split('.') if sentence.strip()]

    # Calculer le nombre de phrases à conserver en fonction du ratio
    num_sentences = int(len(sentences) * ratio)

    # Si le ratio est trop petit, on garde au moins 1 phrase
    num_sentences = max(1, num_sentences)

    # Retourner les phrases les plus importantes (ici, les premières phrases)
    summary = '. '.join(sentences[:num_sentences])

    # Ajouter un point à la fin si nécessaire
    if summary and not summary.endswith('.'):
        summary += '.'

    return summary

def detect_language(text):
    """
    Détecte la langue du texte.
    :param text: Texte dont la langue doit être détectée.
    :return: Code de la langue détectée (ex : 'en', 'fr').
    """
    try:
        return detect(text)
    except Exception as e:
        print(f"Erreur lors de la détection de la langue : {e}")
        return 'en'  # Langue par défaut

# text to speech


# Variables globales
is_paused = False
is_speaking = False  # Pour suivre l'état de la parole


# Fonction pour exécuter la parole avec gestion de thread
def run_speech():
    global is_speaking
    with lock:  # Utiliser un verrou pour garantir qu'un seul thread exécute runAndWait() à la fois
        is_speaking = True
        engine.runAndWait()  # Exécute la lecture
        is_speaking = False

# Fonction pour reprendre la parole
def resume_speech():
    global is_paused, is_speaking
    if is_paused:
        is_paused = False
        if not is_speaking:
            # Démarrer un nouveau thread pour la parole si aucun n'est en cours
            threading.Thread(target=run_speech).start()
        return "Speech resumed."
    else:
        return "Speech is not paused."

# Fonction pour arrêter la parole
def stop_speech():
    global is_paused, is_speaking
    engine.stop()  # Arrêter complètement la parole
    is_paused = False
    is_speaking = False
    return "Speech stopped."

# Fonction pour mettre en pause la parole
def pause_speech():
    global is_paused
    if not is_paused:
        engine.stop()  # Arrêter la lecture en cours
        is_paused = True
        return "Speech paused."
    else:
        return "Speech is already paused."

# Fonction pour lire le texte à haute voix
def text_to_speech(text):
    global is_paused, is_speaking
    try:
        if is_paused:
            resume_speech()  # Reprendre immédiatement la parole si en pause

        engine.say(text)  # Ajouter le texte à la file d'attente de la synthèse vocale

        if not is_speaking:
            # Démarrer la parole dans un thread séparé si aucun thread n'est actif
            threading.Thread(target=run_speech).start()

    except Exception as e:
        print(f"Erreur : {e}")
        return {"error": str(e)}, 500

