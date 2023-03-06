import unittest
from core.utils.common import powershell_return_code


class TestPowershell(unittest.TestCase):
    def test_powershell_return_code(self):
        powershell_script = """if ((Get-ItemProperty HKLM:Software\Classes\Word.Application\CurVer).'(default)') {
          exit 0
        } else {
          exit 1
        }"""
        return_code = powershell_return_code(powershell_script)
        self.assertIn(return_code, [0, 1])

    def test_powershell_output(self):
        pass


if __name__ == '__main__':
    unittest.main()
