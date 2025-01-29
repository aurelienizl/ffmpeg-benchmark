import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_results(csv_file):
    """
    Traite les résultats du benchmark et affiche un résumé simple
    pour utime_s (CPU user time), rtime_s (wall-clock),
    et maxrss_kb (max resident set size).
    """
    summary = {}
    try:
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["codec"], row["preset"], row["bitrate"], row["acceleration"])
                if key not in summary:
                    summary[key] = {
                        "total_utime": 0,
                        "total_rtime": 0,
                        "total_rss": 0,
                        "count": 0
                    }
                try:
                    summary[key]["total_utime"] += float(row["utime_s"])
                    summary[key]["total_rtime"] += float(row["rtime_s"])
                    summary[key]["total_rss"] += float(row["maxrss_kb"])
                    summary[key]["count"] += 1
                except ValueError:
                    logging.warning(f"Valeur invalide dans la ligne: {row}")
                    continue
    except FileNotFoundError:
        logging.error(f"Fichier CSV non trouvé: {csv_file}")
        return
    except Exception as e:
        logging.error(f"Erreur lors de la lecture du fichier CSV: {e}")
        return
    
    logging.info("\n=== Résumé des Résultats (CPU time, wall-clock, maxrss) ===")
    for key, value in summary.items():
        codec, preset, bitrate, acceleration = key
        n = value["count"]
        if n > 0:
            avg_utime = value["total_utime"] / n
            avg_rtime = value["total_rtime"] / n
            avg_rss   = value["total_rss"] / n
        else:
            avg_utime = avg_rtime = avg_rss = 0
        
        logging.info(
            f"Codec: {codec}, Preset: {preset}, Bitrate: {bitrate}, Accélération: {acceleration}\n"
            f"  Temps CPU moyen (utime_s): {avg_utime:.2f}\n"
            f"  Temps total moyen (rtime_s): {avg_rtime:.2f}\n"
            f"  maxrss_kB moyen: {avg_rss:.0f}\n"
        )
