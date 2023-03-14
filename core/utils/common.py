import subprocess
import ctypes
import sys
from io import StringIO
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
    # Make sure cmd output is in English for parsing
    cmd = f"[cultureinfo]::CurrentUICulture = 'en-US'; {cmd}"
    encoded_cmd = powershell_encode(cmd)
    full_cmd = f'powershell -ExecutionPolicy RemoteSigned -e {encoded_cmd}'
    p = subprocess.Popen(full_cmd, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, text=True)
    return p


def python_exec(cmd: str, env: dict) -> dict:
    """Execute python script and return local variables which include: result, exit_code"""
    loc = {}
    exec(cmd, env, loc)
    return loc


def python_run(code: str) -> str:
    """Execute python code and return output"""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(code)
    sys.stdout = old_stdout
    return redirected_output.getvalue()

