import os
import requests

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

# Nombre d'itérations par test
ITERATION_COUNT = 1

def download_videos():
    """
    Télécharge les vidéos de test si elles ne sont pas déjà présentes.
    """
    os.makedirs("samples", exist_ok=True)
    for video in VIDEOS:
        if not os.path.exists(video["file"]):
            print(f"Téléchargement de {video['file']}...")
            try:
                response = requests.get(video["url"], stream=True)
                response.raise_for_status()
                with open(video["file"], "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Download terminé: {video['file']}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors du téléchargement de {video['file']}: {e}")
        else:
            print(f"Fichier déjà présent: {video['file']}")
