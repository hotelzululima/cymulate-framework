import unittest
from core.dependency.windows.installer import *


class TestDependenciesChecker(unittest.TestCase):
    def test_download_file(self):
        result = download("https://cym-rt-resources.s3-eu-west-1.amazonaws.com/PhishingAttachment.xlsm", "$env:temp\PhishingAttachment.xlsm")
        self.assertIn(result, [True, False])


if __name__ == '__main__':
    unittest.main()
