import subprocess
import ctypes
import sys
import tempfile
from io import StringIO
from subprocess import PIPE
from base64 import b64encode


def gain_admin_priv():
    """Gain admin priviledge if not running as admin."""
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def _powershell_encode(cmd: str) -> str:
    """Encode powershell command"""
    return b64encode(cmd.encode('utf_16_le')).decode()


def create_temp_file(content: str) -> str:
    """Create temp file with content"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
    return f.name


def _powershell_adjust(cmd: str) -> str:
    """Adjust powershell command to encode command and let it output english"""
    cmd = f"[cultureinfo]::CurrentUICulture = 'en-US'; {cmd}"
    encoded_cmd = _powershell_encode(cmd)
    return f'chcp 437 > nul & powershell -ExecutionPolicy RemoteSigned -e {encoded_cmd}'


def powershell(cmd: str) -> subprocess.Popen:
    """Return powershell process using subprocess.Popen()"""
    # Make sure output is in English for parsing
    full_cmd = _powershell_adjust(cmd)
    return subprocess.Popen(full_cmd, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, text=True)


def powershell_run(cmd: str, tmp_file_path: str = None) -> subprocess.CompletedProcess:
    """Run powershell command using subprocess.Run()"""
    # Make sure output is in English for parsing
    if tmp_file_path:
        cmd = f'Get-Content {tmp_file_path} | {cmd}'
    full_cmd = _powershell_adjust(cmd)
    return subprocess.run(full_cmd, capture_output=True, shell=True, text=True)


def command_prompt(cmd: str) -> subprocess.Popen:
    """Run command prompt"""
    # Use chcp 437 to make sure cmd output is in English for parsing
    cmd = f"cmd.exe /c chcp 437 > nul \n{cmd}"
    cmd = cmd.replace('\n', ' & ')
    return subprocess.Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True, text=True)


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


def remove_file(file_path: str):
    """Remove file via powershell with force option"""
    powershell_run(f'Remove-Item -Force {file_path}')
