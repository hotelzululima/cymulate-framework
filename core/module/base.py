import json
from core.model.execution import Execution, SuccessIndicator
from dacite import from_dict
from pathlib import Path
from core.utils.log import Log


class BaseModule:
    """Base class for all modules"""

    def __init__(self, execution_id: str, log_level: str = "CUSTOM", input_arguments: dict = None):
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
        self.logger = Log(log_name=execution_id, log_level=log_level).get_logger()
        execution_dict = self.get_execution(execution_id)
        # Deserialize execution json into Execution object
        self.execution = from_dict(data_class=Execution, data=execution_dict)
        # Get input arguments in the format : {argument_name: argument_value}
        self._input_arguments = self.get_input_arguments()
        if input_arguments:
            self._input_arguments.update(input_arguments)

    @property
    def input_arguments(self):
        """Get input arguments"""
        return self._input_arguments

    @input_arguments.setter
    def input_arguments(self, args: dict):
        """Update input arguments"""
        self._input_arguments.update(args)

    @staticmethod
    def get_execution(execution_id: str) -> dict:
        """Get Execution dict from executions json file by id"""
        execution_file = Path(__file__).parent.parent / 'assets/executions.json'
        with open(execution_file, 'r', encoding='utf-8') as f:
            execution_data = json.load(f)
        return next(
            (e for e in execution_data['data'] if e['_id'] == execution_id), None
        )

    def get_enabled_success_indicator(self) -> SuccessIndicator:
        """Get the enabled success indicator"""
        for indicator in self.execution.successIndicators:
            if indicator.enabled:
                return indicator

    def get_input_arguments(self) -> dict:
        """Turn input arguments into a dict"""
        return {arg.name: arg.default[0] for arg in self.execution.inputArguments}

    def resolve_variable(self, command: str, input_arguments: dict = None) -> str:
        """
        Transfer ruby string format from variable name to value
        Ex: Replaces #{test} -> test_value
        """
        input_arguments = input_arguments or self._input_arguments
        for name, value in input_arguments.items():
            command = command.replace(f'#{{{name}}}', value)
        return command

    @staticmethod
    def get_phase_msg(phase: str) -> str:
        """Get formatted phase message"""
        boundary = '*' * len(phase)
        return f'\n{boundary}\n{phase}\n{boundary}'

    def check_dependency(self) -> bool:
        """Check if dependencies are installed"""

    def execute(self):
        """Main execution function"""

    def success_indicate(self) -> bool:
        """Check if the output indicates success"""
        pass

    def cleanup(self):
        """Clean up after the scenario is executed"""
        pass

    def output_parser(self):
        """Parse output result"""
        pass

    def run(self) -> bool:
        """Run the module"""
        self.logger.log("PRINT", '====================')

        success_flag = False
        os_name = ", ".join(self.execution.os)

        module_main_info = f"""{self.execution.name}
-> {self.execution.description}
        """.strip()

        module_brief_info = f"{os_name.upper()} Module : [{self.execution.id}] - \"{self.execution.name}\"".strip()

        module_info = f"""
---
        ID: {self.execution.id}
        Name: {self.execution.name}
        Description: {self.execution.description}
        OS : {os_name}
        Platform: {", ".join(self.execution.supportedPlatforms)}
        Elevation Requirement: {self.execution.executor.elevationRequired}
        Execution Timeout: {self.execution.timeout} minutes
        Tactics: {", ".join([t['name'] for t in self.execution.tactics])}
        Technique: {", ".join([t['name'] for t in self.execution.techniques])}
---
        """.strip()

        self.logger.log("CUSTOM", module_main_info)
        self.logger.success(f"Running {module_brief_info}")
        self.logger.info(module_info)

        # Enter dependency check phase
        self.logger.info(self.get_phase_msg('Dependency Check Phase'))
        if self.check_dependency():
            self.logger.success('All dependency checks passed')

            # Enter execution phase
            self.logger.info(self.get_phase_msg('Execution Phase'))
            self.execute()

            # Enter success indication phase
            self.logger.info(self.get_phase_msg('Success Indication Phase'))
            if self.success_indicate():
                success_flag = True
            else:
                failed_indicators = "\n".join([f' -> {s.description}' for s in self.execution.successIndicators if s.enabled])
                self.logger.error(f'None of below success indicators matched:\n{failed_indicators}')

        else:
            self.logger.error('Module dependency check failed')

        self.logger.info(self.get_phase_msg('Cleanup Phase'))
        self.cleanup()
        return success_flag
