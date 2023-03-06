from core.utils.common import powershell_return_code


def microsoft_office_installed() -> bool:
    """Check if Microsoft Office is installed on the local machine"""
    powershell_script = """if ((Get-ItemProperty HKLM:Software\Classes\Word.Application\CurVer).'(default)') {
  exit 0
} else {
  exit 1
}"""
    return powershell_return_code(powershell_script) == 0


def file_exist(file_path: str) -> bool:
    f"""The file must be present on your drive : {file_path}"""
    powershell_script = f""""if (Test-Path "{file_path}") {{ exit 0}} else {{ exit 1}}"""
    return powershell_return_code(powershell_script) == 0
