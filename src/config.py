import os
import shutil
import subprocess

# Configuration des vidéos à télécharger (H.264 et HEVC)
VIDEOS = [
    {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/1080/Big_Buck_Bunny_1080_10s_30MB.mp4",
        "file": "samples/Big_Buck_Bunny_h264_1080_10s_30MB.mp4",
        "codec": "h264"
    },
    {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h265/1080/Big_Buck_Bunny_1080_10s_30MB.mp4",
        "file": "samples/Big_Buck_Bunny_h265_1080_10s_30MB.mp4",
        "codec": "hevc"
    }
]

# Configuration des presets d'encodage pour H.264 et HEVC
PRESETS = {
    "low": {
        "preset": "veryfast",
        "crf": "28"
    },
    "medium": {
        "preset": "medium",
        "crf": "23"
    },
    "high": {
        "preset": "slow",
        "crf": "18"
    }
}

# Bitrates à tester
BITRATES = ["2M", "4M", "8M"]

# Nombre d'itérations par test (peut être remplacé par un paramètre CLI plus tard)
ITERATION_COUNT = 1

def download_videos():
    """
    Télécharge les vidéos de test si elles ne sont pas déjà présentes,
    en utilisant `wget` ou `curl`.
    """
    os.makedirs("samples", exist_ok=True)

    # Vérifier si `wget` est disponible, sinon essayer `curl`
    wget_path = shutil.which("wget")
    curl_path = shutil.which("curl")

    if not wget_path and not curl_path:
        print("Erreur: ni wget ni curl n'est installé. Impossible de télécharger les fichiers.")
        return

    for video in VIDEOS:
        if not os.path.exists(video["file"]):
            print(f"Téléchargement de {video['file']}...")

            # Construire la commande en fonction de wget ou curl
            if wget_path:
                # wget -O <destination> <url>
                cmd = ["wget", "-O", video["file"], video["url"]]
            else:
                # curl -L -o <destination> <url>
                cmd = ["curl", "-L", "-o", video["file"], video["url"]]

            try:
                subprocess.run(cmd, check=True)
                print(f"Download terminé: {video['file']}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du téléchargement de {video['file']}: {e}")
        else:
            print(f"Fichier déjà présent: {video['file']}")
