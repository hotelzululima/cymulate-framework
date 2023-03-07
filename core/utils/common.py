import subprocess
from subprocess import PIPE, run
from base64 import b64encode


def powershell_encode(cmd: str) -> str:
    """Encode powershell command"""
    return b64encode(cmd.encode('utf_16_le')).decode()

def powershell(cmd: str) -> tuple:
    """Run powershell commands"""
    encoded_cmd = powershell_encode(cmd)
    p = subprocess.Popen(f'powershell -ExecutionPolicy RemoteSigned -e {encoded_cmd}', stdin=PIPE, stderr=PIPE, stdout=PIPE)
    return p.communicate()


def powershell_return_code(cmd: str) -> int:
    """
    Get return code powershell command
    Example: 0 , 1
    """
    encoded_cmd = powershell_encode(cmd)
    p = run(f'powershell -ExecutionPolicy RemoteSigned -e {encoded_cmd}')
    return p.returncode
