"""
Windows module for execution
"""
from core.module.base import BaseModule
from core.model.execution import Dependency, SuccessIndicator
from core.utils.common import powershell, gain_admin_priv, python_exec, python_run, command_prompt, create_temp_file
from typing import List


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str, log_level: str = "SUCCESS"):
        super().__init__(execution_id=execution_id, log_level=log_level)
        self.execution_return_code: int = -1
        self.execution_output: str = ''
        self.execution_output_file: str = ''
        self.output_parser_args = {}

    def check_dependency(self) -> bool:
        failed_dependency = []
        for dependency in self.execution.dependencies:
            if not dependency.enabled:
                continue

            self.logger.info(f'Checking : {dependency.description}')
            if dependency.dependencyExecutorName == 'powershell':
                if self._check_dependency_powershell(dependency):
                    self.logger.success(f'Passed this check: {dependency.description}')
                else:
                    self.logger.error(f'Failed this check: {dependency.description}')
                    failed_dependency.append(dependency.description)
        return not failed_dependency

    def _check_dependency_powershell(self, dependency: Dependency) -> bool:
        """
        Method to check dependency in powershell
        """
        # Get-Pre-req command: DO Download files...etc
        get_pre_req_cmd = self.resolve_variable(dependency.getPrereqCommand)

        self.logger.debug(f'Running Powershell Script: \n{get_pre_req_cmd}\n')
        p = powershell(get_pre_req_cmd)
        out, err = p.communicate()
        result = f"{out}\n\n{err}"
        self.logger.debug(f'Get-Pre-req command result: \n{result}\n')

        # Pre-req command: CHECK Download files...etc
        pre_req_cmd = self.resolve_variable(dependency.prereqCommand)

        p = powershell(pre_req_cmd)
        p.communicate()
        return p.returncode == 0

    @staticmethod
    def _resolve_file_path(variable: str) -> str:
        """
        Resolve absolute path for the variable in powershell
        """
        p = powershell(f'echo {variable}')
        return p.communicate()[0].strip()

    def _set_input_arguments_abs(self):
        """
        Set input_arguments's values to resolve absolute path for the variable in powershell
        """
        input_arguments = self.get_input_arguments()
        for name, value in input_arguments.items():
            if value.startswith('$env'):
                self.input_arguments[name] = self._resolve_file_path(value)

    def execute(self):
        if self.execution.executor.elevationRequired:
            self.logger.info('Elevation required, requesting admin privilege...')
            gain_admin_priv()

        # Not resolving absolute path at init because the temp path might change if evaluated to other users
        self._set_input_arguments_abs()

        script = self.resolve_variable(self.execution.executor.command)
        if self.execution.executor.name == 'powershell':
            self._run_powershell(script)
        elif self.execution.executor.name == 'command_prompt':
            self._run_cmd(script)
        elif self.execution.executor.name == 'python':
            self._run_python(script)

        self.execution_output_file = create_temp_file(self.execution_output)

    def _run_cmd(self, script: str):
        """
        Container to run command prompt script
        """
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        out, err = p.communicate()
        result = f"{out}\n\n{err}"
        self.logger.debug(f'Command Prompt script result: \n{result}\n')
        self.execution_output = out

    def _run_powershell(self, script: str):
        """
        Container to run powershell script
        """
        self.logger.debug(f'Running Powershell Script: \n{script}\n')
        p = powershell(script)
        result_list = p.communicate()
        result = "\n".join(result_list)
        self.logger.debug(f'Powershell script result: \n{result}\n')
        self.execution_output = result_list[0]
        self.execution_return_code = p.returncode

    def _run_python(self, script: str):
        """
        Container to run python script
        """
        self.logger.debug(f'Running Python Script: \n{script}\n')
        self.execution_output = python_run(script)
        self.logger.debug(f'Python script result: \n{self.execution_output}\n')

    @staticmethod
    def _adjust_python_script(script: str) -> str:
        """
        Adjust python script from cymulate format to applicable format
        """
        # Transform script to a function
        python_script = script.replace('exit(0)', 'return 0').replace('exit(1)', 'return 1')
        python_script = "\n    ".join(python_script.splitlines())
        python_script = f"def py_test():\n    {python_script}"

        # Append variable to store exit code at the end
        return f"{python_script}\nexit_code = py_test()"

    def success_indicate(self) -> bool:
        # If no success indicators, check executor's return code
        if not self.execution.successIndicators:
            if self.execution_return_code == 0:
                self.logger.success(f'Executor return code: {self.execution_return_code}')
                return True
            else:
                self.logger.warning(f'Executor return code: {self.execution_return_code}')
                return False

        failed_success_indicators = self._check_success_indicators(self.execution.successIndicators)
        return not failed_success_indicators

    def _check_success_indicators(self, success_indicators: List[SuccessIndicator]) -> List[SuccessIndicator]:
        """Method to check success indicators, return failed success indicators if any"""
        # Record failed success indicators for further use
        failed_success_indicators = []

        for success_indicator in success_indicators:
            # Check all success indicators include disabled since enabled one might fail but disabled ones won't
            script = self.resolve_variable(success_indicator.successIndicatorCommand)

            if success_indicator.successIndicatorExecutor == "powershell":
                if not (is_success := self._success_indicate_powershell(script, success_indicator.pipe)):
                    failed_success_indicators.append(success_indicator)
                self._success_indicator_log(is_success, success_indicator.description)

            elif success_indicator.successIndicatorExecutor == "command_prompt":
                if not (is_success := self._success_indicate_cmd(script, success_indicator.pipe)):
                    failed_success_indicators.append(success_indicator)
                self._success_indicator_log(is_success, success_indicator.description)

            elif success_indicator.successIndicatorExecutor == "python":
                if not (is_success := self._success_indicate_python(script, success_indicator.pipe)):
                    failed_success_indicators.append(success_indicator)
                self._success_indicator_log(is_success, success_indicator.description)

        return failed_success_indicators

    def _success_indicator_log(self, is_success: bool, description: str):
        """
        Method to wrap the logging output of success indicator
        """
        if is_success:
            self.logger.success(f'Success Indicator: {description}')
        else:
            self.logger.warning(f'Failed Success Indicator: {description}')

    def _success_indicate_powershell(self, script: str, pipe: bool) -> bool:
        """
        Method to check if execution succeeded by powershell script
        """
        self.logger.debug(f'Running Powershell Script: \n{script}\n')

        # Check if indicator needs to pipe the output of the execution
        if pipe:
            script = f"Get-Content \"{self.execution_output_file}\" | {script}"

        p = powershell(script)
        out, err = p.communicate()
        self.logger.debug(f'Powershell script result: \n{out}\n{err}\n')
        return p.returncode == 0

    def _success_indicate_python(self, script: str, pipe: bool) -> bool:
        """
        Method to check if execution succeeded by python script
        """
        python_script = self._adjust_python_script(script)
        self.logger.debug(f'Running Python Script: \n{python_script}\n')

        # Add piped output to the environment
        env = {'piped_output': self.execution_output} | globals()

        result = python_exec(python_script, env)
        self.logger.debug(f'Python script result: \n{result}\n')

        # Check if the function does not return 1, since some scripts might return None or 0 for success
        return result.get('exit_code') != 1

    def _success_indicate_cmd(self, script: str, pipe: bool) -> bool:
        """
        Method to check if execution succeeded by command prompt script
        """
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        p.communicate()
        self.logger.debug(f'Command Prompt script return code: {p.returncode}\n')
        return p.returncode == 0

    def output_parser(self):
        """
        Method to parse the output of the execution
        """
        if not self.execution.outputParser:
            self.logger.debug(f'No output parser, using raw output: \n{self.execution_output}\n')
            return

        script = self.resolve_variable(self.execution.outputParser.outputParserCommand)
        # Save the parsed output which maps suitable input arguments for other modules to use
        for output_parser in self.execution.outputParsers:
            if output_parser.outputParserExecutor == "powershell":
                self._output_parser_powershell(output_parser.pipe, script)

            elif output_parser.outputParserExecutor == "command_prompt":
                self._output_parser_cmd(output_parser.pipe, script)

            elif output_parser.outputParserExecutor == "python":
                self._output_parser_python(output_parser.pipe, script)

    def _output_parser_powershell(self, pipe: bool, script: str):
        """
        Method to parse the output of the execution by powershell script
        """
        self.logger.debug(f'Running Powershell Script: \n{script}\n')
        p = powershell(script)
        out, err = p.communicate()
        self.logger.debug(f'Powershell script result: \n{out}\n{err}\n')
        self.execution_output = out

    def _output_parser_python(self, pipe: bool, script: str):
        """
        Method to parse the output of the execution by python script
        """
        python_script = self._adjust_python_script(script)
        self.logger.debug(f'Running Python Script: \n{python_script}\n')

        # Add piped output to the environment
        env = {'piped_output': self.execution_output} | globals()

        result = python_exec(python_script, env)
        self.logger.debug(f'Python script result: \n{result}\n')
        self.execution_output = result

    def _output_parser_cmd(self, pipe: bool, script: str):
        """
        Method to parse the output of the execution by command prompt script
        """
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        p.communicate()
        self.logger.debug(f'Command Prompt script return code: {p.returncode}\n')
        self.execution_output = p.returncode
