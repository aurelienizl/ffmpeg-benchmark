# main.py

import csv
from download import download_test_videos
from detection import detect_cpu_vendor, check_hw_acceleration
from transcoding import run_benchmark
from config import TRANSCODING_SCENARIOS, BITRATES, ITERATION_COUNT, SOURCE_VIDEOS
import os

def main():
    """
    Point d'entrée principal du benchmark.
    """
    # 1. Téléchargement des vidéos
    print("=== Téléchargement des vidéos de test ===")
    downloaded_videos = download_test_videos()

    # 2. Détection du CPU et de l'accélération matérielle
    cpu_vendor = detect_cpu_vendor()
    hw_accel = check_hw_acceleration(cpu_vendor)
    print(f"\n=== CPU détecté : {cpu_vendor} ===")
    print(f"=== Accélération matérielle détectée : {hw_accel} ===\n")

    # 3. Calcul du Nombre Total de Tests
    total_tests = len(SOURCE_VIDEOS) * len(TRANSCODING_SCENARIOS) * len(BITRATES) * ITERATION_COUNT
    print(f"Total des tests à exécuter : {total_tests}\n")
    print("Voici les combinaisons de tests :\n")

    # Afficher toutes les combinaisons
    test_number = 1
    for source_video in SOURCE_VIDEOS:
        source_codec = source_video["codec"]
        for scenario in TRANSCODING_SCENARIOS:
            target_codec, target_container, preset = scenario
            for bitrate in BITRATES:
                for iteration in range(ITERATION_COUNT):
                    print(f"{test_number}. Source Codec: {source_codec}, Target Codec: {target_codec}, "
                          f"Container: {target_container}, Preset: {preset}, Bitrate: {bitrate}, Iteration: {iteration+1}")
                    test_number += 1

    confirmation = input("\nVoulez-vous continuer avec ces tests ? (o/n): ").strip().lower()
    if confirmation != 'o':
        print("Benchmarking annulé par l'utilisateur.")
        return

    # 4. Exécution des benchmarks
    results = []

    for source_video in downloaded_videos:
        print(f"\n=== Traitement du fichier vidéo : {source_video} ===\n")
        # Trouver le codec source
        source_codec = next((video["codec"] for video in SOURCE_VIDEOS if video["file"] == source_video), "unknown")
        for scenario in TRANSCODING_SCENARIOS:
            target_codec, target_container, preset = scenario
            for bitrate in BITRATES:
                for iteration in range(ITERATION_COUNT):
                    print(f">>> Test: {source_codec} → {target_codec}, container={target_container}, "
                          f"bitrate={bitrate}, preset={preset}, iteration={iteration+1}")
                    avg_time, all_times, avg_fps, all_fps = run_benchmark(
                        source_file=source_video,
                        target_codec=target_codec,
                        bitrate=bitrate,
                        accel_type=hw_accel,
                        preset=preset,
                        iteration=ITERATION_COUNT
                    )

                    print(f"\nDurées mesurées: {all_times} (sec)")
                    print(f"Durée moyenne : {avg_time:.2f} sec")
                    print(f"FPS moyen : {avg_fps} fps")
                    print("-" * 40)

                    results.append({
                        "cpu_vendor": cpu_vendor,
                        "hw_accel": hw_accel,
                        "source_file": source_video,
                        "source_codec": source_codec,
                        "target_codec": target_codec,
                        "target_container": target_container,
                        "preset": preset,
                        "bitrate": bitrate,
                        "avg_time_s": avg_time,
                        "all_times_s": all_times,
                        "avg_fps": avg_fps,
                        "all_fps": all_fps
                    })

    # 5. Sauvegarde des résultats dans un CSV
    csv_file = "benchmark_results.csv"
    with open(csv_file, "w", newline="") as f:
        fieldnames = [
            "cpu_vendor", "hw_accel", "source_file", "source_codec", "target_codec",
            "target_container", "preset", "bitrate", "avg_time_s", "all_times_s",
            "avg_fps", "all_fps"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nLes résultats de benchmark sont enregistrés dans: {csv_file}")
    print("Fin du script.")

if __name__ == "__main__":
    main()
