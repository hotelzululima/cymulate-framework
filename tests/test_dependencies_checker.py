import unittest
from core.module.windows.dependency.checker import *


class TestDependenciesChecker(unittest.TestCase):
    def test_microsoft_office_installed(self):
        result = microsoft_office_installed()
        self.assertIn(result, [True, False])

    @unittest.mock.patch('sys.stdout')
    def test_file_exist(self):
        result = file_exist("$env:temp\wsu8257.tmp")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
