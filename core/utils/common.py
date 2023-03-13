import subprocess
import ctypes
import sys
from subprocess import PIPE
from base64 import b64encode


def gain_admin_priv():
    """Gain admin priviledge if not running as admin."""
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def powershell_encode(cmd: str) -> str:
    """Encode powershell command"""
    return b64encode(cmd.encode('utf_16_le')).decode()


def powershell(cmd: str) -> subprocess.Popen:
    """Return powershell process"""
    encoded_cmd = powershell_encode(cmd)
    p = subprocess.Popen(f'powershell -ExecutionPolicy RemoteSigned -e {encoded_cmd}', stdin=PIPE, stderr=PIPE,
                         stdout=PIPE)
    return p


