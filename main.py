"""
Entry point for the framework.
"""
import sys
import core.template.apt34 as apt34
from core.module.windows import WindowsModule

if __name__ == '__main__':
    if len(sys.argv) == 2:
        WindowsModule(sys.argv[1], debug=True).run()
    else:
        apt34.start()

