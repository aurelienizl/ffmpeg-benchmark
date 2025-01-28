# transcoding.py

import os
import time
import subprocess
from utils import extract_fps, calculate_fps

def build_ffmpeg_command(source_file, target_file, accel_type, source_codec, target_codec, bitrate, preset, presets_config):
    """
    Construit la commande FFmpeg pour transcoder de source_codec à target_codec.
    """
    command = ["ffmpeg", "-y", "-hide_banner", "-i", source_file]

    # Définir le codec vidéo cible et les paramètres selon le preset
    if accel_type == "none":
        if target_codec in ["h264", "hevc", "av1", "vp8", "vp9"]:
            codec_ffmpeg = get_ffmpeg_codec(target_codec)
            preset_options = presets_config[preset].get(target_codec, {})

            if target_codec in ["h264", "hevc", "av1"]:
                command += [
                    "-c:v", codec_ffmpeg,
                    "-preset", preset_options.get("preset", "medium"),
                    "-crf", preset_options.get("crf", "23"),
                    "-b:v", bitrate
                ]
            elif target_codec == "vp8":
                command += [
                    "-c:v", codec_ffmpeg,
                    "-cpu-used", preset_options.get("cpu-used", "3"),
                    "-crf", preset_options.get("crf", "30"),
                    "-b:v", bitrate
                ]
            elif target_codec == "vp9":
                command += [
                    "-c:v", codec_ffmpeg,
                    "-speed", preset_options.get("speed", "3"),
                    "-crf", preset_options.get("crf", "30"),
                    "-b:v", bitrate
                ]
        else:
            raise ValueError(f"Codec cible non supporté : {target_codec}")

    elif accel_type in ["intel_vaapi", "amd_vaapi"]:
        if target_codec in ["h264", "hevc"]:
            codec_ffmpeg = get_ffmpeg_codec(target_codec)
        else:
            raise ValueError(f"Codec cible non supporté avec VAAPI : {target_codec}")

        # Configurer VAAPI
        if accel_type == "intel_vaapi":
            init_hw_device = "vaapi=intel:/dev/dri/renderD128"
            filter_hw_device = "intel"
        elif accel_type == "amd_vaapi":
            init_hw_device = "vaapi=amd:/dev/dri/renderD128"
            filter_hw_device = "amd"

        command += [
            "-init_hw_device", init_hw_device,
            "-filter_hw_device", filter_hw_device,
            "-vf", "format=nv12,hwupload",
            "-c:v", codec_ffmpeg,
            "-b:v", bitrate
        ]

    else:
        raise ValueError(f"Type d'accélération matérielle non supporté : {accel_type}")

    # Définir le fichier de sortie
    command += [target_file]

    return command

def get_ffmpeg_codec(target_codec):
    """
    Retourne le codec FFmpeg correspondant au codec cible.
    """
    codec_mapping = {
        "h264": "libx264",
        "hevc": "libx265",
        "vp8": "libvpx",
        "vp9": "libvpx-vp9",
        "av1": "libaom-av1"
    }
    return codec_mapping.get(target_codec, "libx264")  # Fallback

def get_target_container(target_codec):
    """
    Retourne le container cible en fonction du codec cible.
    """
    codec_to_container = {
        "h264": "mp4",
        "hevc": "mp4",
        "vp8": "webm",
        "vp9": "webm",
        "av1": "mp4"
    }
    return codec_to_container.get(target_codec, "mp4")  # Fallback

def get_extension(container):
    """
    Retourne l'extension de fichier en fonction du container.
    """
    container_to_extension = {
        "mp4": "mp4",
        "webm": "webm",
        "mkv": "mkv"
    }
    return container_to_extension.get(container, "mp4")  # Fallback

def run_benchmark(source_file, target_codec, bitrate, accel_type, preset, iteration=1):
    """
    Lance le transcodage plusieurs fois et mesure le temps et les FPS.
    Retourne la durée moyenne, les temps, les FPS moyens et les FPS détaillés.
    """
    from config import PRESETS  # Importer les presets depuis config.py
    times = []
    fps_list = []

    for i in range(iteration):
        # Définir le nom du fichier de sortie
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        # Déterminer l'extension du fichier cible en fonction du container
        target_container = get_target_container(target_codec)
        output_extension = get_extension(target_container)
        output_file = f"temp_{base_name}_{target_codec}_{bitrate}_{preset}_{i}.{output_extension}"

        # Construire la commande FFmpeg
        command = build_ffmpeg_command(
            source_file=source_file,
            target_file=output_file,
            accel_type=accel_type,
            source_codec=get_source_codec(source_file),
            target_codec=target_codec,
            bitrate=bitrate,
            preset=preset,
            presets_config=PRESETS
        )

        # Afficher la commande exécutée
        print(f"\nCommande FFmpeg #{i+1} : {' '.join(command)}")

        # Lancer FFmpeg et capturer la sortie stderr
        start_time = time.perf_counter()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stderr = ""
        while True:
            line = process.stderr.readline()
            if not line:
                break
            stderr += line

        process.wait()
        end_time = time.perf_counter()

        elapsed = end_time - start_time
        times.append(elapsed)

        # Extraire FPS depuis la sortie de FFmpeg
        fps = extract_fps(stderr)
        if fps is not None:
            fps_list.append(fps)
            print(f" -> FPS : {fps:.2f}")
        else:
            # Calculer FPS si non détecté
            fps = calculate_fps(source_file, elapsed)
            if fps is not None:
                fps_list.append(fps)
                print(f" -> FPS calculé : {fps:.2f}")
            else:
                fps_list.append("Non détecté")
                print(" -> FPS : Non détecté")

        # Nettoyer le fichier de sortie temporaire
        if os.path.exists(output_file):
            os.remove(output_file)

    # Calculer les moyennes
    avg_time = sum(times) / len(times)

    # Calculer la moyenne des FPS en ignorant les 'Non détecté'
    valid_fps = [f for f in fps_list if isinstance(f, float)]
    if valid_fps:
        avg_fps = sum(valid_fps) / len(valid_fps)
    else:
        avg_fps = "Non détecté"

    return avg_time, times, avg_fps, fps_list

def get_source_codec(source_file):
    """
    Déduit le codec source en fonction du nom du fichier.
    (Basé sur la convention de nommage dans config.py)
    """
    if "h264" in source_file.lower():
        return "h264"
    elif "hevc" in source_file.lower() or "h265" in source_file.lower():
        return "hevc"
    elif "av1" in source_file.lower():
        return "av1"
    elif "vp8" in source_file.lower():
        return "vp8"
    elif "vp9" in source_file.lower():
        return "vp9"
    else:
        # Fallback : utiliser ffprobe pour déterminer le codec
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=nokey=1:noprint_wrappers=1",
            source_file
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            codec = result.stdout.strip()
            if codec in ["h264", "hevc", "vp8", "vp9", "av1"]:
                return codec
            else:
                return "unknown"
        except:
            return "unknown"
