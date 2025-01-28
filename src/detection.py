# detection.py

import platform
import sys
import os

def detect_cpu_vendor():
    """
    Détecte si le CPU est Intel ou AMD, sinon renvoie 'Unknown'.
    Basé sur platform.processor() et /proc/cpuinfo.
    """
    cpu_str = platform.processor().lower()
    if 'intel' in cpu_str:
        return 'Intel'
    elif 'amd' in cpu_str:
        return 'AMD'
    else:
        if sys.platform.startswith("linux"):
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    info = f.read().lower()
                    if 'intel' in info:
                        return 'Intel'
                    elif 'amd' in info:
                        return 'AMD'
            except:
                pass
        return 'Unknown'

def check_hw_acceleration(cpu_vendor):
    """
    Vérifie si un device /dev/dri/renderD128 est présent (VAAPI).
    - Si Intel et /dev/dri/renderD128 => 'intel_vaapi'
    - Si AMD et /dev/dri/renderD128 => 'amd_vaapi'
    - Sinon => 'none'
    """
    render_device = "/dev/dri/renderD128"
    if os.path.exists(render_device):
        if cpu_vendor == "Intel":
            return "intel_vaapi"
        elif cpu_vendor == "AMD":
            return "amd_vaapi"
    return "none"
