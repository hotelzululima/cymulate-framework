class BaseModule:
    """
    base class for all modules
    """
    def __init__(self):
        """
        Name: Module Name
        Description: Module Description
        OS : Windows, Linux, Mac, Android, iOS
        Platform: Powershell, Python
        Elevation Requirement: Admin, User
        Execution Timeout: 5 minute
        Tactics: Initial Access, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact
        Technique: ATT&CK Technique
        """
        self.name = ""
        self.description = ""
        self.os = ""
        self.platform = ""
        self.elevation_requirement = ""
        self.execution_timeout = 0
        self.tactics = []
        self.technique = []
