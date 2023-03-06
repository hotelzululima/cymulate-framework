import subprocess
from subprocess import PIPE, run


def powershell(cmd: str) -> tuple:
    """Run powershell commands"""
    p = subprocess.Popen(f'powershell {cmd}', stdin=PIPE, stderr=PIPE, stdout=PIPE)
    return p.communicate()


def powershell_return_code(cmd: str) -> int:
    """
    Get return code powershell command
    Example: 0 , 1
    """
    p = run(f'powershell {cmd}')
    return p.returncode
