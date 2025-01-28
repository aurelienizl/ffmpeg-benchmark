# utils.py

import re
import subprocess

def extract_fps(ffmpeg_output):
    """
    Extrait la valeur de fps de la sortie de FFmpeg.
    Recherche la dernière occurrence de 'fps=XX.X'.
    """
    fps_pattern = re.compile(r"fps=\s*([\d.]+)")
    fps_matches = fps_pattern.findall(ffmpeg_output)
    if fps_matches:
        return float(fps_matches[-1])
    return None

def calculate_fps(input_file, elapsed_time):
    """
    Calcule les FPS en fonction du nombre de frames et du temps écoulé.
    Utilise ffprobe pour obtenir le nombre total de frames.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-count_frames",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames",
        "-of", "default=nokey=1:noprint_wrappers=1",
        input_file
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        total_frames = int(result.stdout.strip())
        fps = total_frames / elapsed_time
        return fps
    except:
        return None
