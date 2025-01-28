# ffmpeg-benchmark

## Aperçu

Le **Benchmark de Transcodage Vidéo** est un outil basé sur Python conçu pour évaluer et comparer les performances des codecs vidéo **H.264** et **HEVC (H.265)**. En utilisant FFmpeg, cet outil exécute une série de tests de transcodage avec différents presets et bitrates, fournissant des informations précieuses sur la vitesse d'encodage et les FPS (Frames Per Second).

## Fonctionnalités

- **Comparaison de Codecs** : Compare les performances des codecs H.264 et HEVC (H.265).
- **Variations de Presets et Bitrates** : Tests sur plusieurs presets (`low`, `medium`, `high`) et bitrates (`2M`, `4M`, `8M`).
- **Téléchargement Automatisé** : Télécharge automatiquement les vidéos d'échantillon pour les tests.
- **Détection du CPU et Accélération Matérielle** : Détecte le type de CPU et vérifie la disponibilité de l'accélération matérielle (par exemple, VAAPI).
- **Résultats Complets** : Enregistre les résultats des benchmarks dans un fichier CSV pour une analyse ultérieure.

## Installation

### Prérequis

- **Système d'Exploitation** : Linux (recommandé)
- **Python** : Version 3.6 ou supérieure
- **FFmpeg** : Doit être installé et accessible depuis la ligne de commande

### Installer FFmpeg

Vérifiez si FFmpeg est installé :

```bash
ffmpeg -version
```

Si FFmpeg n'est pas installé, installez-le via le gestionnaire de paquets :

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Installer les Dépendances Python

Installez les bibliothèques Python nécessaires :

```bash
pip3 install pandas matplotlib seaborn
```

## Configuration

Toutes les configurations sont définies dans le fichier `config.py`. Par défaut, le projet est configuré pour comparer les codecs **H.264** et **HEVC (H.265)** à travers différents presets et bitrates.

### Exemple de Configuration

```python
# config.py

import itertools

# 1. Définir les combinaisons de codecs cibles et containers
TARGET_SCENARIOS = [
    ("h264", "mp4"),
    ("hevc", "mp4"),
    ("h264", "mkv"),
    ("hevc", "mkv"),
]

# 2. Définir les presets avec paramètres spécifiques pour chaque codec cible
PRESETS = {
    "low": {
        "h264": {"preset": "veryfast", "crf": "28"},
        "hevc": {"preset": "veryfast", "crf": "28"},
    },
    "medium": {
        "h264": {"preset": "medium", "crf": "23"},
        "hevc": {"preset": "medium", "crf": "23"},
    },
    "high": {
        "h264": {"preset": "slow", "crf": "18"},
        "hevc": {"preset": "slow", "crf": "18"},
    }
}

# 3. Définir les bitrates à tester
BITRATES = ["2M", "4M", "8M"]

# 4. Nombre d'itérations par test
ITERATION_COUNT = 1

# 5. Définir les vidéos sources avec leurs codecs et containers
SOURCE_VIDEOS = [
    {
        # MP4 ( H.264 )
        "file": "samples/mp4.h264.1080p.30mb.mp4",
        "codec": "h264",
        "container": "mp4",
        "url": "https://test-videos.co.uk/vids/jellyfish/mp4/h264/1080/Jellyfish_1080_10s_30MB.mp4"
    },
    {
        # MP4 ( H.265 )
        "file": "samples/mp4.hevc.1080p.30mb.mp4",
        "codec": "hevc",
        "container": "mp4",
        "url": "https://test-videos.co.uk/vids/jellyfish/mp4/h265/1080/Jellyfish_1080_10s_30MB.mp4"
    },
]

# 6. Générer les scénarios de transcodage (sans inclure le codec source)
TRANSCODING_SCENARIOS = [
    (target_codec, target_container, preset)
    for (target_codec, target_container) in TARGET_SCENARIOS
    for preset in PRESETS.keys()
]
```

### Explications des Modifications

- **TARGET_SCENARIOS** : Inclut uniquement les combinaisons des codecs **H.264** et **HEVC** avec les containers **mp4** et **mkv**.
- **PRESETS** : Définition des presets `low`, `medium`, et `high` avec les paramètres spécifiques pour chaque codec.
- **SOURCE_VIDEOS** : Seules les vidéos **H.264** et **HEVC** sont incluses, stockées dans le dossier `samples/`.

## Utilisation

### Étape 1 : Télécharger les Vidéos Sources

Le script principal (`main.py`) gère automatiquement le téléchargement des vidéos sources définies dans `config.py`. Assurez-vous que le dossier `samples/` existe ou sera créé par le script.

### Étape 2 : Exécuter le Benchmark

Lancez le script principal pour démarrer le processus de benchmarking.

```bash
python3 main.py
```

Lors de l'exécution, le script :

1. Télécharge les vidéos sources (si elles ne sont pas déjà présentes).
2. Détecte le type de CPU et vérifie la disponibilité de l'accélération matérielle.
3. Affiche le nombre total de tests et les combinaisons de tests.
4. Demande une confirmation pour commencer les tests.
5. Exécute les benchmarks de transcodage.
6. Enregistre les résultats dans `benchmark_results.csv`.

## Description des Scripts

### `main.py`

Point d'entrée principal du benchmark. Ordonne le téléchargement des vidéos, la détection du CPU, l'exécution des benchmarks et l'enregistrement des résultats.

### `download.py`

Télécharge les vidéos sources définies dans `config.py` dans le dossier `samples/`.

### `detection.py`

Détecte le type de CPU (Intel ou AMD) et vérifie la disponibilité de l'accélération matérielle (VAAPI).

### `transcoding.py`

Construit et exécute les commandes FFmpeg pour chaque scénario de transcodage. Mesure le temps d'encodage et les FPS.

### `config.py`

Contient les configurations principales du benchmark, y compris les vidéos sources, les scénarios cibles, les presets et les bitrates.

### `utils.py`

Fournit des fonctions utilitaires pour extraire les FPS de la sortie de FFmpeg et calculer les FPS si nécessaire.


## Résultats et Interprétation

Le fichier `benchmark_results.csv` contient les colonnes suivantes :

| cpu_vendor | hw_accel | source_file               | source_codec | target_codec | target_container | preset | bitrate | avg_time_s | all_times_s           | avg_fps | all_fps              |
|------------|----------|---------------------------|--------------|--------------|-------------------|--------|---------|------------|-----------------------|---------|----------------------|
| Intel      | none     | samples/mp4.h264.mp4      | h264         | h264         | mp4               | low    | 2M      | 11.00      | [11.00]               | 27.00   | [27.00]              |
| Intel      | none     | samples/mp4.h264.mp4      | h264         | h264         | mp4               | low    | 4M      | 12.00      | [12.00]               | 27.00   | [27.00]              |
| ...        | ...      | ...                       | ...          | ...          | ...               | ...    | ...     | ...        | ...                   | ...     | ...                  |

### Description des Colonnes

- **cpu_vendor** : Type de CPU détecté (e.g., Intel, AMD, Unknown)
- **hw_accel** : Type d'accélération matérielle utilisée (e.g., intel_vaapi, amd_vaapi, none)
- **source_file** : Chemin du fichier vidéo source
- **source_codec** : Codec du fichier source (h264, hevc)
- **target_codec** : Codec cible pour le transcodage (h264, hevc)
- **target_container** : Container cible pour le transcodage (mp4, mkv)
- **preset** : Preset d'encodage (low, medium, high)
- **bitrate** : Bitrate utilisé pour le transcodage (2M, 4M, 8M)
- **avg_time_s** : Temps moyen d'encodage en secondes
- **all_times_s** : Liste des temps d'encodage pour chaque itération
- **avg_fps** : FPS moyen calculé à partir des itérations
- **all_fps** : Liste des FPS détectés pour chaque itération

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez ajouter de nouvelles fonctionnalités ou corriger des bugs, veuillez ouvrir une issue ou soumettre une pull request.

## Licence

Ce projet est sous licence UNLICENSE. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

Pour toute question ou support, veuillez me contacter aurelien.izoulet@epita.fr
