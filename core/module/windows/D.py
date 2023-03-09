from core.module.base.BaseModule import BaseModule
from core.dependency.windows.checker import microsoft_office_installed, file_exist
from core.dependency.windows.installer import download


class DownloadAndExecutePhishingAttachment(BaseModule):
    """
    Name:
        Download and Execute Phishing Attachment - VBScript
    Description:
        Downloads a macro-enabled Excel file to a given path and executes it.
         The file contains a VBScript that opens the default web browser and creates a file at $env:TEMP\vbs_success.txt.
    ATT&CK Tactics:
        TA0001 - Initial Access
        TA0003 - Persistence
    ATT&CK Technique:
        T1566.001 - Spearphishing Attachment
        T1137.001 - Office Template Macros
    """

    def __init__(self):
        _id = "62385f03a0e69ed2274622cc"
        super().__init__(execution_id=_id)

    def run(self):
        powershell_script = """$excel = New-Object -comobject Excel.Application

$FilePath = '$env:temp\PhishingAttachment.xlsm'
$workbook = $excel.Workbooks.Open($FilePath)

$excel.Visible = $true

$app = $excel.Application
$app.Run("ThisWorkbook.RunAndGetCmd")

Write-Host "If successful, chrome.exe process will start."""
        powershell_script = """function Get-ChildProcesses ($ParentProcessId) {
$filter = "parentprocessid = '$($ParentProcessId)'"
Get-CIMInstance -ClassName win32_process -filter $filter | Foreach-Object {
        $_
        if ($_.ParentProcessId -ne $_.ProcessId) {
            Get-ChildProcesses $_.ProcessId
        }
    }
}
$Global:Processes = Get-WMIObject -Class Win32_Process
$Global:Processes | %{if ($_.processName -eq 'EXCEL.EXE') {if (Get-ChildProcesses $_.ProcessId | where {$_.processName -eq 'chrome.exe'}){exit 0}}}
exit 1"""

    def cleanup(self):
        """The following code is used to clean up after the scenario or restore a state that was changed."""
        powershell_script = """Stop-Process -Name "Excel" -Force
Sleep 5
Remove-Item $env:temp\PhishingAttachment.xlsm -Force"""

    def is_success(self):
        """Checks if a chrome.exe process was created under an EXCEL.EXE process (macro)"""

    def install_dependencies(self):
        """Install dependencies and check before running"""
        # Check if Microsoft Office is installed
        ## Preempt Installation
        ## Check
        test1 = microsoft_office_installed()
        if not test1:
            print(f"Failed the check:\n{test1.__doc__}\n")
        # The file must be present on your drive
        ## Preempt Installation
        result = download(self.execution.download_file_url, self.execution.download_file_path)
        # if not test2:
        #     print(f"Failed the check:\n{test2.__doc__}\n)

    def check_dependencies(self):
        """Check dependency before running"""
        test1 = microsoft_office_installed()
        if not test1:
            print(f"Failed the check:\n{test1.__doc__}\n")
        test2 = file_exist("%temp%/wsu8257.tmp")
        if not test2:
            print(f"Failed the check:\n{test2.__doc__}\n")

    def output_parser(self, output):
        """Parse the final output of the module"""
        pass