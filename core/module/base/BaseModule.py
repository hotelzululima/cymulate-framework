import json
from core.model.execution import Execution
from dacite import from_dict
from pathlib import Path

class BaseModule:
    """
    Base class for all modules
    """

    def __init__(self, execution_id: str):
        """
        Name: Module Name
        Description: Module Description
        OS : Windows, Linux, Mac, Android, iOS
        Platform: Powershell, Python
        Elevation Requirement: True, False
        Execution Timeout: N minutes
        Tactics: ID of MITRE ATT&CK Tactics
        Technique: ID of MITRE ATT&CK Technique
        """
        self.execution_id = execution_id
        execution_dict = self.get_execution(execution_id)
        self.execution = from_dict(data_class=Execution, data=execution_dict)

    def get_execution(self, execution_id: str) -> dict:
        """
        Get Execution dict from executions json file by id
        """
        execution_file = Path(__file__).parent.parent.parent / 'assets/executions.json'
        with open(execution_file, 'r', encoding='utf-8') as f:
            execution_data = json.load(f)
        execution = next((e for e in execution_data['data'] if e['_id'] == execution_id), None)
        return execution

    def run(self):
        """
        The following code is used to run the scenario.
        """
        pass

    def cleanup(self):
        """
        The following code is used to clean up after the scenario or restore a state that was changed.
        """
        pass

