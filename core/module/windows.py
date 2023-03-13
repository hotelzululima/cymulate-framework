"""
Windows module for execution
"""

from core.module.base import BaseModule
from core.utils.common import powershell


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
                self.logger.debug(f'Running Powershell Script: {get_pre_req_cmd}\n')
                p = powershell(get_pre_req_cmd)
                result = "\n".join([r.decode('big5') for r in p.communicate()])
                self.logger.debug(f'Get-Pre-req command result: {result}\n')

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
        return p.communicate()[0].decode('big5').strip()

    def set_input_arguments_abs(self):
        """
        Set input_arguments's values to resolve absolute path for the variable in powershell
        """
        input_arguments = self.get_input_arguments()
        for name, value in input_arguments.items():
            if value.startswith('$env'):
                self.input_arguments[name] = self.resolve_file_path(value)

    def execute(self):
        if self.execution.executor.name == 'powershell':
            # Not resolving absolute path at init because the temp path might change if evaluated to other users
            self.set_input_arguments_abs()
            powershell_script = self.resolve_variable(self.execution.executor.command)
            self.logger.debug(f'Running Powershell Script: {powershell_script}\n')
            p = powershell(powershell_script)
            result_list = p.communicate()
            result = "\n".join([r.decode('big5') for r in result_list])
            self.logger.debug(f'Powershell script result: {result}\n')

        self.execution_output = result_list[0].decode('big5')
        self.execution_return_code = p.returncode

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
            if success_indicator.successIndicatorExecutor == "powershell":
                powershell_script = self.resolve_variable(success_indicator.successIndicatorCommand)
                self.logger.debug(f'Running Powershell Script: {powershell_script}\n')
                p = powershell(powershell_script)
                result = p.communicate()
                self.logger.debug(f'Powershell script result: {result}\n')
                if p.returncode == 0:
                    self.logger.success(f'Success Indicator: {success_indicator.description}')
                    return True
                else:
                    self.logger.warning(f'Failed Success Indicator: {success_indicator.description}')
        return False
