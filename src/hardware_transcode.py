import subprocess
import os
import logging
import re
from config import PRESETS, BITRATES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_available_gpus():
    """
    Lists all available GPU render devices.
    Returns a list of device paths, e.g., ['/dev/dri/renderD128', '/dev/dri/renderD129']
    """
    dri_dir = "/dev/dri"
    try:
        devices = os.listdir(dri_dir)
        render_devices = [os.path.join(dri_dir, dev) for dev in devices if re.match(r'renderD\d+', dev)]
        if not render_devices:
            logging.warning("Aucun GPU VAAPI trouvé dans /dev/dri.")
        else:
            logging.info(f"GPUs VAAPI disponibles: {', '.join(render_devices)}")
        return render_devices
    except Exception as e:
        logging.error(f"Erreur lors de la liste des GPUs: {e}")
        return []

def check_available_gpus(gpus):
    """
    Execute the command: ffmpeg -init_hw_device vaapi=foo:/dev/dri/{gpu}
    Check if the selected GPU can be used for VAAPI hardware transcoding.
    Returns a list of usable GPUs.
    """
    usable_gpus = []

    for gpu in gpus:
        try:
            result = subprocess.run(
                ["ffmpeg", "-init_hw_device", f"vaapi=foo:{gpu}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                logging.info(f"Hardware device at {gpu} cannot be used for hardware acceleration using VAAPI.")
                usable_gpus.append(gpu)
            else:
                logging.warning(f"Hardware device at {gpu} can be used for hardware acceleration using VAAPI.")
        except Exception as e:
            logging.error(f"There is no available devices for VAAPI hardware acceleration")

    return usable_gpus

def build_hardware_command(source, target, codec, bitrate, preset, gpu):
    # (same as before)
    codec_map = {
        "h264": "h264_vaapi",
        "hevc": "hevc_vaapi"
    }
    cmd = [
        "ffmpeg",
        "-benchmark",
        "-y", "-hide_banner",
        "-i", source,
        "-init_hw_device", f"vaapi=hw:/dev/dri/{gpu}",
        "-filter_hw_device", "hw",
        "-vf", "format=nv12,hwupload",
        "-c:v", codec_map.get(codec, "h264_vaapi"),
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

def transcode_hardware(source, codec, gpu = "renderD128", iteration_count=1):
    """
    Effectue le transcodage matériel pour un codec donné (H.264 ou HEVC).
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
                cmd = build_hardware_command(source, target_file, codec, bitrate, preset, gpu)
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
