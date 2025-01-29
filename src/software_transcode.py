import subprocess
import os
import logging
import re
from config import PRESETS, BITRATES
# Removed ITERATION_COUNT import, because we'll pass it in as a function parameter.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_software_command(source, target, codec, bitrate, preset):
    # (same as before)
    codec_map = {
        "h264": "libx264",
        "hevc": "libx265"
    }

    cmd = [
        "ffmpeg",
        "-benchmark",
        "-y", "-hide_banner",
        "-i", source,
        "-c:v", codec_map.get(codec, "libx264"),
        "-preset", PRESETS[preset]["preset"],
        "-crf", PRESETS[preset]["crf"],
        "-b:v", bitrate,
        target
    ]
    return cmd

def extract_metrics(stderr):
    # (same as before)
    metrics = {
        'utime_s': 0.0,
        'rtime_s': 0.0,
        'maxrss_kb': 0
    }
    # parse utime, rtime, maxrss...
    bench_match = re.search(
        r'bench:\s*utime=([\d\.]+)s\s*stime=([\d\.]+)s\s*rtime=([\d\.]+)s',
        stderr
    )
    if bench_match:
        try:
            metrics['utime_s'] = float(bench_match.group(1))
            metrics['rtime_s'] = float(bench_match.group(3))
        except ValueError:
            pass

    rss_match = re.search(r'bench:\s*maxrss=(\d+)kB', stderr)
    if rss_match:
        try:
            metrics['maxrss_kb'] = int(rss_match.group(1))
        except ValueError:
            pass

    return metrics

def transcode_software(source, codec, iteration_count=1):
    """
    Effectue le transcodage logiciel pour un codec donné (H.264 ou HEVC).
    On répète chaque test 'iteration_count' fois.
    """
    results = []
    os.makedirs("transcoded_outputs", exist_ok=True)

    for preset in PRESETS:
        for bitrate in BITRATES:
            for i in range(iteration_count):
                target_file = (
                    f"transcoded_outputs/"
                    f"{os.path.basename(source).replace('.mp4','')}_{codec}_{bitrate}_{preset}_{i}.mp4"
                )
                cmd = build_software_command(source, target_file, codec, bitrate, preset)
                logging.info(f"Exécution de la commande: {' '.join(cmd)}")

                try:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate()

                    metrics = extract_metrics(stderr)

                    results.append({
                        "source": source,
                        "codec": codec,
                        "preset": preset,
                        "bitrate": bitrate,
                        "iteration": i + 1,
                        "utime_s": metrics['utime_s'],
                        "rtime_s": metrics['rtime_s'],
                        "maxrss_kb": metrics['maxrss_kb']
                    })

                    logging.info(
                        f"Terminé: {target_file} - "
                        f"utime_s={metrics['utime_s']:.2f}, "
                        f"rtime_s={metrics['rtime_s']:.2f}, "
                        f"maxrss_kb={metrics['maxrss_kb']}"
                    )
                except Exception as e:
                    logging.error(f"Exception lors du transcodage de {target_file}: {e}")

                if os.path.exists(target_file):
                    os.remove(target_file)

    return results
