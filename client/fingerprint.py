import hashlib
import platform
import subprocess
import sys
import uuid


def _get_mac_address() -> str:
    node = uuid.getnode()
    if node >> 40 & 1:
        return ""
    return format(node, "x")


def _get_disk_serial_windows() -> str:
    raw = subprocess.check_output(
        "wmic diskdrive get serialnumber", shell=True
    ).decode()
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    return lines[1] if len(lines) > 1 else ""


def _get_disk_serial_linux() -> str:
    try:
        devices = subprocess.check_output(
            "lsblk -dno NAME,TYPE | awk '$2==\"disk\"{print $1}'", shell=True
        ).decode().splitlines()
        device = devices[0].strip() if devices else "sda"
        return subprocess.check_output(
            f"blkid -s UUID -o value /dev/{device}", shell=True
        ).decode().strip()
    except Exception:
        return ""


def _get_disk_serial() -> str:
    try:
        if sys.platform == "win32":
            return _get_disk_serial_windows()
        return _get_disk_serial_linux()
    except Exception:
        return ""


def _get_cpu_identifier() -> str:
    return platform.processor()


def get_fingerprint() -> str:
    mac = _get_mac_address()
    disk = _get_disk_serial()
    cpu = _get_cpu_identifier()
    raw = f"{mac}|{disk}|{cpu}"
    return hashlib.sha256(raw.encode()).hexdigest()
