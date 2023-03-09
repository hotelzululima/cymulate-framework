from core.module.base.BaseModule import BaseModule


class WindowsModule(BaseModule):
    def __init__(self, execution_id: str):
        super().__init__(execution_id)

    def run(self):
        pass

    def cleanup(self):
        pass

    def is_success(self):
        pass

    def install_dependencies(self):
        pass