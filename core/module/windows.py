"""
Windows module for execution
"""

from core.module.base import BaseModule
from core.model.execution import Dependency
from core.utils.common import powershell, gain_admin_priv, python_exec, python_run, command_prompt, create_temp_file


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str, debug: bool = True):
        super().__init__(execution_id=execution_id, debug=debug)
        self.execution_return_code: int = -1
        self.execution_output: str = ''
        self.execution_output_file: str = ''

    def check_dependency(self) -> bool:
        failed_dependency = []
        for dependency in self.execution.dependencies:
            if not dependency.enabled:
                continue

            self.logger.info(f'Checking : {dependency.description}')
            if dependency.dependencyExecutorName == 'powershell':
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
                is_dependency_installed = (p.returncode == 0)
                if not is_dependency_installed:
                    self.logger.error(f'Failed this check: {dependency.description}')
                    failed_dependency.append(dependency.description)
                else:
                    self.logger.success(f'Passed this check: {dependency.description}')
        return not failed_dependency

    @staticmethod
    def resolve_file_path(variable: str) -> str:
        """
        Resolve absolute path for the variable in powershell
        """
        p = powershell(f'echo {variable}')
        return p.communicate()[0].strip()

    def set_input_arguments_abs(self):
        """
        Set input_arguments's values to resolve absolute path for the variable in powershell
        """
        input_arguments = self.get_input_arguments()
        for name, value in input_arguments.items():
            if value.startswith('$env'):
                self.input_arguments[name] = self.resolve_file_path(value)

    def execute(self):
        if self.execution.executor.elevationRequired:
            self.logger.info('Elevation required, requesting admin privilege...')
            gain_admin_priv()

        # Not resolving absolute path at init because the temp path might change if evaluated to other users
        self.set_input_arguments_abs()

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

        for success_indicator in self.execution.successIndicators:
            script = self.resolve_variable(success_indicator.successIndicatorCommand)

            if success_indicator.successIndicatorExecutor == "powershell":
                self.logger.debug(f'Running Powershell Script: \n{script}\n')

                # Check if indicator needs to pipe the output of the execution
                if success_indicator.pipe:
                    script = f"Get-Content \"{self.execution_output_file}\" | {script}"

                p = powershell(script)
                out, err = p.communicate()
                self.logger.debug(f'Powershell script result: \n{out}\n{err}\n')

                if p.returncode == 0:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')

            elif success_indicator.successIndicatorExecutor == "command_prompt":
                self.logger.debug(f'Running Command Prompt Script: \n{script}\n')
                p = command_prompt(script)
                p.communicate()
                self.logger.debug(f'Command Prompt script return code: {p.returncode}\n')

                if p.returncode == 0:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')

            elif success_indicator.successIndicatorExecutor == "python":
                python_script = self._adjust_python_script(script)
                self.logger.debug(f'Running Python Script: \n{python_script}\n')

                # Add piped output to the environment
                env = {'piped_output': self.execution_output} | globals()

                result = python_exec(python_script, env)
                self.logger.debug(f'Python script result: \n{result}\n')

                # Check if the function does not return 1, since some scripts might return None or 0 for success
                if result.get('exit_code') != 1:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')
        return False
