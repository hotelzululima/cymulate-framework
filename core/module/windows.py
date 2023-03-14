"""
Windows module for execution
"""

from core.module.base import BaseModule
from core.utils.common import powershell, gain_admin_priv, python_exec, python_run


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str, debug: bool = True):
        super().__init__(execution_id=execution_id, debug=debug)
        self.execution_return_code: int = -1
        self.execution_output: str = ''

    def check_dependency(self) -> bool:
        failed_dependency = []
        for dependency in self.execution.dependencies:
            self.logger.info(f'Checking : {dependency.description}')
            if dependency.dependencyExecutorName == 'powershell':
                # Get-Pre-req command: Download files...etc
                get_pre_req_cmd = self.resolve_variable(dependency.getPrereqCommand)
                self.logger.debug(f'Running Powershell Script: \n{get_pre_req_cmd}\n')
                p = powershell(get_pre_req_cmd)
                result = "\n".join([r.decode('utf-8') for r in p.communicate()])
                self.logger.debug(f'Get-Pre-req command result: \n{result}\n')

                # Get-Pre-req command: Download files...etc
                pre_req_cmd = self.resolve_variable(dependency.prereqCommand)
                p = powershell(pre_req_cmd)
                p.communicate()
                is_dependency_installed = (p.returncode == 0)
                if not is_dependency_installed:
                    self.logger.error(f'Failed this check: {dependency.description}')
                    failed_dependency.append(dependency.description)
                else:
                    self.logger.success(f'Passed this check: {dependency.description}')
        return len(failed_dependency) == 0

    @staticmethod
    def resolve_file_path(variable: str) -> str:
        """
        Resolve absolute path for the variable in powershell
        """
        p = powershell(f'echo {variable}')
        return p.communicate()[0].decode('utf-8').strip()

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
            self.logger.debug(f'Running Powershell Script: \n{script}\n')
            p = powershell(script)
            result_list = p.communicate()
            result = "\n".join([r.decode('utf-8') for r in result_list])
            self.logger.debug(f'Powershell script result: \n{result}\n')
            self.execution_output = result_list[0].decode('utf-8')
            self.execution_return_code = p.returncode

        elif self.execution.executor.name == 'python':
            self.logger.debug(f'Running Python Script: \n{script}\n')
            out = python_run(script)
            self.logger.debug(f'Python script result: \n{out}\n')
            self.execution_output = out

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
                p = powershell(script)
                result = p.communicate()
                self.logger.debug(f'Powershell script result: {result}\n')
                if p.returncode == 0:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')
            elif success_indicator.successIndicatorExecutor == "python":
                # Make script to a function
                python_script = script.replace('exit(0)', '  return 0').replace('exit(1)', 'return 1')
                python_script = "\n    ".join(python_script.splitlines())
                python_script = f"def py_test():\n    {python_script}"
                # Append variable assignment to the python script at the end
                python_script = python_script + "\nexit_code = py_test()"

                self.logger.debug(f'Running Python Script: \n{python_script}\n')
                # Add piped output to the environment
                env = {'piped_output': self.execution_output}
                env.update(globals())

                result = python_exec(python_script, env)
                self.logger.debug(f'Python script result: \n{result}\n')
                # Check if the function does not return 1, since some scripts might return None or 0 for success
                if result.get('exit_code') != 1:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')

        return False
