"""
Windows Dependencies Utils
"""
from core.utils.common import powershell


def download(download_file_url: str, download_file_path: str):
    """Download a file from a given url to a given path."""
    powershell_script = f"""[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
$systemProxy = [System.Net.WebRequest]::GetSystemWebproxy()
$systemProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials
$proxy = $systemProxy.GetProxy("{download_file_url}")
if ($proxy.AbsoluteUri -ne "{download_file_url}"){{
    Invoke-WebRequest {download_file_url} -OutFile "{download_file_path}" -Proxy $proxy -ProxyUseDefaultCredentials
}}else {{
    Invoke-WebRequest {download_file_url} -OutFile "{download_file_path}"
}}"""
    result = powershell(powershell_script)
    return result


