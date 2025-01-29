# vaapi_detect.py

import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_vainfo_output():
    """
    Exécute la commande 'vainfo' et retourne la sortie.
    """
    try:
        result = subprocess.run(["vainfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de l'exécution de vainfo : {e.stderr}")
        return ""
    except FileNotFoundError:
        logging.error("vainfo n'est pas installé. Veuillez l'installer pour la détection VAAPI.")
        return ""

def parse_vainfo_for_vaapi(vainfo_output):
    """
    Analyse la sortie de vainfo et vérifie si H.264 / HEVC encSlice est supporté.
    Retourne un dictionnaire:
      {
        "h264_encode": bool,
        "h264_decode": bool,
        "hevc_encode": bool,
        "hevc_decode": bool
      }
    """
    profiles = {}
    for line in vainfo_output.split('\n'):
        line = line.strip()
        # Example lines:
        # VAProfileH264Main               : VAEntrypointVLD
        # VAProfileH264Main               : VAEntrypointEncSlice
        # VAProfileHEVCMain               : VAEntrypointEncSlice
        if line.startswith("VAProfile"):
            parts = line.split(':')
            if len(parts) < 2:
                continue
            profile = parts[0].strip()
            entrypoints = [ep.strip() for ep in parts[1].split(',')]
            if profile not in profiles:
                profiles[profile] = []
            profiles[profile].extend(entrypoints)

    def has_enc_slice(profile_keys):
        # If any of these profiles exist with "VAEntrypointEncSlice" or similar
        # This indicates encode support
        for prof in profile_keys:
            if prof in profiles:
                for ep in profiles[prof]:
                    if "EncSlice" in ep or "EncPicture" in ep:
                        return True
        return False

    def has_decode_slice(profile_keys):
        # If "VAEntrypointVLD" is present
        for prof in profile_keys:
            if prof in profiles:
                if any("VLD" in ep for ep in profiles[prof]):
                    return True
        return False

    # Check for H.264
    h264_profile_keys = [
        "VAProfileH264Main",
        "VAProfileH264High",
        "VAProfileH264ConstrainedBaseline"
    ]
    h264_encode = has_enc_slice(h264_profile_keys)
    h264_decode = has_decode_slice(h264_profile_keys)

    # Check for HEVC
    hevc_profile_keys = [
        "VAProfileHEVCMain",
        "VAProfileHEVCMain10"
    ]
    hevc_encode = has_enc_slice(hevc_profile_keys)
    hevc_decode = has_decode_slice(hevc_profile_keys)

    return {
        "h264_encode": h264_encode,
        "h264_decode": h264_decode,
        "hevc_encode": hevc_encode,
        "hevc_decode": hevc_decode,
    }

def get_encoding_capabilities():
    """
    Vérifie s'il existe un support VAAPI pour H.264 et HEVC, peu importe le vendor (Intel/AMD).
    """
    vainfo_output = get_vainfo_output()
    if not vainfo_output:
        # vainfo failed or not installed => no hardware encode
        return {
            "h264_encode": False,
            "h264_decode": False,
            "hevc_encode": False,
            "hevc_decode": False,
        }

    capabilities = parse_vainfo_for_vaapi(vainfo_output)
    return capabilities
