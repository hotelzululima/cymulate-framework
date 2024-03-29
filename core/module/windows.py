"""
Windows module for execution
"""
from core.module.base import BaseModule
from core.model.execution import Dependency, SuccessIndicator
from core.utils.common import powershell, gain_admin_priv, python_exec, python_run, command_prompt, powershell_run, \
    create_temp_file, remove_file
from typing import List


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str, log_level: str = "CUSTOM", input_arguments: dict = None):
        super().__init__(execution_id=execution_id, log_level=log_level, input_arguments=input_arguments)
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
        """Method to check dependency in powershell"""
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
        """Resolve absolute path for the variable in powershell"""
        p = powershell(f'echo {variable}')
        return p.communicate()[0].strip()

    def _set_input_arguments_abs(self):
        """Set input_arguments's values to resolve absolute path for the variable in powershell"""
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
        """Method to run command prompt script"""
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        out, err = p.communicate()
        result = f"{out}\n\n{err}"
        self.logger.debug(f'Command Prompt script result: \n{result}\n')
        self.execution_output = out

    def _run_powershell(self, script: str):
        """Method to run powershell script"""
        self.logger.debug(f'Running Powershell Script: \n{script}\n')
        p = powershell(script)
        result_list = p.communicate()
        result = "\n".join(result_list)
        self.logger.debug(f'Powershell script result: \n{result}\n')
        self.execution_output = result_list[0]
        self.execution_return_code = p.returncode

    def _run_python(self, script: str):
        """Method to run python script"""
        self.logger.debug(f'Running Python Script: \n{script}\n')
        self.execution_output = python_run(script)
        self.logger.debug(f'Python script result: \n{self.execution_output}\n')

    @staticmethod
    def _adjust_python_script(script: str) -> str:
        """Adjust python script from cymulate format to applicable format"""
        # Transform script to a function
        python_script = script.replace('exit(0)', 'return 0').replace('exit(1)', 'return 1')
        python_script = "\n    ".join(python_script.splitlines())
        python_script = f"def py_test():\n    {python_script}"

        # Append variable to store exit code at the end
        return f"{python_script}\nexit_code = py_test()"

    def success_indicate(self) -> bool:
        # If no success indicators, check executor's return code
        success_flag = False
        if self.execution.successIndicators:
            success_flag = self._check_success_indicators(self.execution.successIndicators)
        elif success_flag := self.execution_return_code == 0:
            msg = f'Success Indicator: Executor return code: {self.execution_return_code}'
            self.logger.success(msg)
            self.logger.log("CUSTOM", msg)
        else:
            self.logger.error(f'Failed Success Indicator: Executor return code: {self.execution_return_code}')
        # Remove execution output file in temp folder
        remove_file(self.execution_output_file)
        return success_flag

    def _check_success_indicators(self, success_indicators: List[SuccessIndicator]) -> bool:
        """Method to check success indicators"""
        # Return true if any success indicator is true
        for success_indicator in success_indicators:
            is_success = False

            # Check all success indicators include disabled ones since enabled ones might fail but disabled ones won't
            script = self.resolve_variable(success_indicator.successIndicatorCommand)

            if success_indicator.successIndicatorExecutor == "powershell":
                is_success = self._success_indicate_powershell(script, success_indicator.pipe)
                self._success_indicator_log(is_success, success_indicator.description)

            elif success_indicator.successIndicatorExecutor == "command_prompt":
                is_success = self._success_indicate_cmd(script, success_indicator.pipe)
                self._success_indicator_log(is_success, success_indicator.description)

            elif success_indicator.successIndicatorExecutor == "python":
                is_success = self._success_indicate_python(script, success_indicator.pipe)
                self._success_indicator_log(is_success, success_indicator.description)

            if is_success:
                return True

        # If no success indicator succeeded, return false
        return False

    def _success_indicator_log(self, is_success: bool, description: str):
        """Method to wrap the logging output of success indicator"""
        if is_success:
            self.logger.success(f'Success Indicator: {description}')
            self.logger.log("CUSTOM", f'Success Indicator: {description}')
        else:
            self.logger.warning(f'Failed Success Indicator: {description}')

    def _success_indicate_powershell(self, script: str, pipe: bool) -> bool:
        """Method to check if execution succeeded by powershell script"""
        self.logger.debug(f'Running Powershell Script: \n{script}\n')

        # Check if indicator needs to pipe the output of the execution
        output_file = self.execution_output_file if pipe else None

        result = powershell_run(script, output_file)
        self.logger.debug(f'Powershell script result: \n{result.stdout}\n{result.stderr}\n')
        return result.returncode == 0

    def _success_indicate_python(self, script: str, pipe: bool) -> bool:
        """Method to check if execution succeeded by python script"""
        python_script = self._adjust_python_script(script)
        self.logger.debug(f'Running Python Script: \n{python_script}\n')

        # Add piped output to the environment
        env = {'piped_output': self.execution_output} | globals()

        result = python_exec(python_script, env)
        self.logger.debug(f'Python script result: \n{result}\n')

        # Check if the function return 0 or None, since some scripts will return 0 or None for success
        # Example: ID: 5fb4ec71181932cc0f4ad6cf | name: Base64 Encode a file (Windows)
        return result["exit_code"] in {0, None}

    def _success_indicate_cmd(self, script: str, pipe: bool) -> bool:
        """Method to check if execution succeeded by command prompt script"""
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        p.communicate()
        self.logger.debug(f'Command Prompt script return code: {p.returncode}\n')
        return p.returncode == 0

    def output_parser(self):
        """Method to parse the output of the execution"""
        if not self.execution.outputParser:
            self.logger.debug(f'No output parser, using raw output: \n{self.execution_output}\n')
            return

        script = self.resolve_variable(self.execution.outputParser.outputParserCommand)
        # Save the parsed output which maps suitable input arguments for other modules to use
        for output_parser in self.execution.outputParsers:
            if not output_parser.enabled:
                continue

            if output_parser.outputParserExecutor == "powershell":
                self._output_parser_powershell(output_parser.pipe, script)

            elif output_parser.outputParserExecutor == "command_prompt":
                self._output_parser_cmd(output_parser.pipe, script)

            elif output_parser.outputParserExecutor == "python":
                self._output_parser_python(output_parser.pipe, script)

    def _output_parser_powershell(self, pipe: bool, script: str):
        """Method to parse the output of the execution by powershell script"""
        output_file = self.execution_output_file if pipe else None
        self.logger.debug(f'Running Powershell Script: \n{script}\n')
        result = powershell_run(script, output_file)
        self.logger.debug(f'Powershell script result: \n{result.stdout}\n{result.stderr}\n')

    def _output_parser_python(self, pipe: bool, script: str):
        """Method to parse the output of the execution by python script"""
        python_script = self._adjust_python_script(script)
        self.logger.debug(f'Running Python Script: \n{python_script}\n')

        # Add piped output to the environment
        env = {'piped_output': self.execution_output} | globals()

        result = python_exec(python_script, env)
        self.logger.debug(f'Python script result: \n{result}\n')
        self.execution_output = result

    def _output_parser_cmd(self, pipe: bool, script: str):
        """Method to parse the output of the execution by command prompt script"""
        self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
        p = command_prompt(script)
        p.communicate()
        self.logger.debug(f'Command Prompt script return code: {p.returncode}\n')
        self.execution_output = p.returncode
