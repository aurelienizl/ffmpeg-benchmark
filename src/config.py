# config.py

import itertools

""" # 1. Définir les combinaisons de codecs cibles et containers
TARGET_SCENARIOS = [
    ("h264", "mp4"),
    ("hevc", "mp4"),
    ("vp8", "webm"),
    ("vp9", "webm"),
    ("h264", "mkv"),
    ("av1", "mp4"),  # Ajout du scénario AV1 avec container MP4
] """

""" # 2. Définir les presets avec paramètres spécifiques pour chaque codec cible
PRESETS = {
    "low": {
        "h264": {"preset": "veryfast", "crf": "28"},
        "hevc": {"preset": "veryfast", "crf": "28"},
        "vp8": {"cpu-used": "5", "crf": "35"},    # Paramètres VP8
        "vp9": {"speed": "5", "crf": "35"},
        "av1": {"preset": "veryfast", "crf": "28"},  # Preset AV1
    },
    "medium": {
        "h264": {"preset": "medium", "crf": "23"},
        "hevc": {"preset": "medium", "crf": "23"},
        "vp8": {"cpu-used": "3", "crf": "30"},    # Paramètres VP8
        "vp9": {"speed": "3", "crf": "30"},
        "av1": {"preset": "medium", "crf": "23"},  # Preset AV1
    },
    "high": {
        "h264": {"preset": "slow", "crf": "18"},
        "hevc": {"preset": "slow", "crf": "18"},
        "vp8": {"cpu-used": "1", "crf": "25"},    # Paramètres VP8
        "vp9": {"speed": "1", "crf": "25"},
        "av1": {"preset": "slow", "crf": "18"},   # Preset AV1
    }
}
 """
""" # 3. Définir les bitrates à tester
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
    {
        # WebM ( VP8 )
        "file": "samples/webm.vp8.1080p.30mb.webm",
        "codec": "vp8",
        "container": "webm",
        "url": "https://test-videos.co.uk/vids/jellyfish/webm/vp8/1080/Jellyfish_1080_10s_30MB.webm"
    },
    {
        # WebM ( VP9 )
        "file": "samples/webm.vp9.1080p.30mb.webm",
        "codec": "vp9",
        "container": "webm",
        "url": "https://test-videos.co.uk/vids/jellyfish/webm/vp9/1080/Jellyfish_1080_10s_30MB.webm"
    },
    {
        # MKV ( H.264 )
        "file": "samples/mkv.h264.1080p.30mb.mkv",
        "codec": "h264",
        "container": "mkv",
        "url": "https://test-videos.co.uk/vids/jellyfish/mkv/1080/Jellyfish_1080_10s_30MB.mkv"
    },
    {
        # AV1 ( AV1 )
        "file": "samples/av1.av1.1080p.30mb.mp4",  
        "codec": "av1",
        "container": "mp4",
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/av1/1080/Big_Buck_Bunny_1080_10s_30MB.mp4"
    },
]

# 6. Générer les scénarios de transcodage (sans inclure le codec source)
TRANSCODING_SCENARIOS = [
    (target_codec, target_container, preset)
    for (target_codec, target_container) in TARGET_SCENARIOS
    for preset in PRESETS.keys()
]
 """

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
