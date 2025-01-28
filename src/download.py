# download.py

import os
import subprocess
from config import SOURCE_VIDEOS

def download_file(url, output_file):
    """
    Télécharge un fichier depuis une URL vers un fichier local.
    Utilise 'wget' pour le téléchargement.
    """
    if not os.path.exists(output_file):
        print(f"Téléchargement en cours : {url} -> {output_file}")
        try:
            subprocess.run(["wget", "-O", output_file, url], check=True)
            print("Téléchargement terminé.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du téléchargement de {url}: {e}")
    else:
        print(f"Fichier déjà présent : {output_file}")

def download_test_videos():
    """
    Télécharge toutes les vidéos définies dans SOURCE_VIDEOS dans le dossier 'samples'.
    """
    samples_dir = "samples"
    os.makedirs(samples_dir, exist_ok=True)  # Crée le dossier 'samples' s'il n'existe pas

    for video in SOURCE_VIDEOS:
        output_path = os.path.join(samples_dir, os.path.basename(video["file"]))
        download_file(video["url"], output_path)

    # Retourne la liste des fichiers vidéo téléchargés avec le chemin complet
    return [os.path.join(samples_dir, video["file"].split('/')[-1]) for video in SOURCE_VIDEOS]
