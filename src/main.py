import os
import csv
import logging
import argparse
import platform
from config import download_videos, VIDEOS
from vaapi_detect import get_encoding_capabilities
from software_transcode import transcode_software
from hardware_transcode import transcode_hardware
from result_process import process_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Benchmark de Transcodage Vidéo avec FFmpeg")

    # Mutually exclusive arguments for software/hardware
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--software', action='store_true', help='Exécute uniquement le benchmark logiciel')
    group.add_argument('--hardware', action='store_true', help='Exécute uniquement le benchmark matériel')

    # New argument for iteration count
    parser.add_argument('--iteration-count', type=int, default=1,
                        help='Nombre d’itérations pour chaque test (défaut: 1)')

    return parser.parse_args()

def main():
    args = parse_arguments()
    clear_console()

    logging.info("=== Benchmark de Transcodage Vidéo ===")

    # Always detect CPU capabilities
    logging.info("=== Détection des Capacités du CPU ===")
    capabilities = get_encoding_capabilities()
    logging.info("Capacités d'encodage/décodage détectées :")
    for key, value in capabilities.items():
        logging.info(f"  {key}: {'Oui' if value else 'Non'}")

    # If no arguments, just show capabilities and exit
    if not (args.software or args.hardware):
        logging.info("Aucun benchmark demandé. Fin du programme.")
        return

    # If we are doing either hardware or software, we need the sample videos
    logging.info("=== Téléchargement des vidéos de test ===")
    download_videos()

    all_results = []

    # --software mode
    if args.software:
        logging.info("=== Début du Transcodage Logiciel ===")
        for video in VIDEOS:
            source = video["file"]
            codec = video["codec"]
            logging.info(f"--- Transcodage logiciel de {source} avec codec {codec} ---")

            # Pass the iteration count to transcode_software
            results = transcode_software(source, codec, iteration_count=args.iteration_count)
            for entry in results:
                entry["acceleration"] = "software"
            all_results.extend(results)

    # --hardware mode
    elif args.hardware:
        if not (capabilities.get("h264_encode") or capabilities.get("hevc_encode")):
            logging.info("=== Encodage matériel non supporté sur ce système ===")
        else:
            logging.info("=== Début du Transcodage Matériel ===")
            for video in VIDEOS:
                source = video["file"]
                codec = video["codec"]
                # Check if hardware is supported for the given codec
                if codec == "h264" and capabilities.get("h264_encode"):
                    logging.info(f"--- Transcodage matériel de {source} avec codec {codec} ---")
                    results = transcode_hardware(source, codec, iteration_count=args.iteration_count)
                    for entry in results:
                        entry["acceleration"] = "vaapi"
                    all_results.extend(results)
                elif codec == "hevc" and capabilities.get("hevc_encode"):
                    logging.info(f"--- Transcodage matériel de {source} avec codec {codec} ---")
                    results = transcode_hardware(source, codec, iteration_count=args.iteration_count)
                    for entry in results:
                        entry["acceleration"] = "vaapi"
                    all_results.extend(results)
                else:
                    logging.info(f"--- Transcodage matériel de {source} avec codec {codec} ignoré (non supporté) ---")

    # Save results to CSV
    if not all_results:
        logging.warning("Aucun résultat de benchmark à enregistrer.")
    else:
        logging.info("=== Enregistrement des Résultats ===")
        csv_file = "benchmark_results.csv"
        try:
            with open(csv_file, "w", newline="") as f:
                fieldnames = [
                    "source",
                    "codec",
                    "preset",
                    "bitrate",
                    "iteration",
                    "utime_s",
                    "rtime_s",
                    "maxrss_kb",
                    "acceleration"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in all_results:
                    writer.writerow(result)
            logging.info(f"Les résultats de benchmark sont enregistrés dans : {csv_file}")
        except Exception as e:
            logging.error(f"Erreur lors de l'écriture du fichier CSV : {e}")

        logging.info("=== Traitement des Résultats ===")
        process_results(csv_file)
        logging.info("Benchmark terminé.")

if __name__ == "__main__":
    main()
