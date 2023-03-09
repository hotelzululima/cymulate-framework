import json
from core.model.execution import Execution
from dacite import from_dict
from pathlib import Path
from core.utils.log import Log
from core.utils.common import powershell, powershell_return_code


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
        self.logger = Log(log_name='module', log_level='DEBUG').get_logger()
        self.execution_id = execution_id
        execution_dict = self.get_execution(execution_id)
        # Deserialize execution dict into Execution object
        self.execution = from_dict(data_class=Execution, data=execution_dict)
        # Replace variable name in powershell script to actual value
        self.input_arguments = self.get_input_arguments()

    @staticmethod
    def get_execution(execution_id: str) -> dict:
        """
        Get Execution dict from executions json file by id
        """
        execution_file = Path(__file__).parent.parent.parent / 'assets/executions.json'
        with open(execution_file, 'r', encoding='utf-8') as f:
            execution_data = json.load(f)
        execution = next((e for e in execution_data['data'] if e['_id'] == execution_id), None)
        return execution

    def get_input_arguments(self) -> dict:
        """
        Turn input arguments into a dict
        """
        return {arg.name: arg.default[0] for arg in self.execution.inputArguments}

    def check_dependency(self) -> bool:
        """
        Check if dependencies are installed
        """
        for dependency in self.execution.dependencies:
            self.logger.info(f'Checking : {dependency.description}')
            if dependency.dependencyExecutorName == 'powershell':
                get_pre_req_cmd = self.replace_input_arguments(dependency.getPrereqCommand)
                result = powershell(get_pre_req_cmd)
                self.logger.debug(f'Get-Pre-req command result: {result}\n')
                pre_req_cmd = self.replace_input_arguments(dependency.prereqCommand)
                is_dependency_installed = powershell_return_code(pre_req_cmd) == 0
                if not is_dependency_installed:
                    self.logger.error(f'\nFailed this check: {dependency.description}')
                    return False

        self.logger.success('All dependency checks passed')
        return True

    def replace_input_arguments(self, command: str) -> str:
        """
        Replace input arguments in command -> name: value
        """
        for name, value in self.input_arguments.items():
            command = command.replace(f'#{{{name}}}', value)
        return command

    def resolve_file_path(self, file_path: str) -> str:
        """
        Resolve file path if it is a variable
        """
        return powershell(f'echo {file_path}')[0].decode('big5').strip()

    def execute(self):
        """
        Main execution function
        """
        if self.execution.executor.name == 'powershell':
            # Not resolving absolute path at init because the temp path might change if evaluated to other users
            for name, value in self.input_arguments.items():
                if value.startswith('$env'):
                    self.input_arguments[name] = self.resolve_file_path(value)

            powershell_script = self.replace_input_arguments(self.execution.executor.command)
            self.logger.debug(f'Running Powershell Script: {powershell_script}\n')
            result_list = powershell(powershell_script)
            result = "\n".join([r.decode('big5') for r in result_list])
            self.logger.debug(f'Powershell script result: {result}\n')

    def cleanup(self):
        """
        Clean up after the scenario
        """
        pass
