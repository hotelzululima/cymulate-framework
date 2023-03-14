from core.module.windows import WindowsModule


if __name__ == '__main__':
    # Advanced Scenario - APT 34 (OilRig)

    # Download and Execute Phishing Attachment - VBScript
    # m = WindowsModule("62385f03a0e69ed2274622cc", debug=False)
    # m.run()

    # Invoke Raw Powershell command
    # m = WindowsModule("628263ae9bad2dfa4b66d4c6")
    # m.run()

    # Scheduled Task - Persistance
    # m = WindowsModule("60f43effac529a1c1f25ebdc", debug=True)
    # m.run()

    # Load .NET assembly
    # TODO: Failed to load assembly
    # m = WindowsModule("6249bc4d414705609848bab6", debug=True)
    # m.run()

    # BASE64 ENCODE A FILE (WINDOWS)
    # m = WindowsModule("5fb4ec71181932cc0f4ad6cf", debug=True)
    # m.run()

    # Sandbox Evasion: Time Based Evasion (Sleep)
    # m = WindowsModule("5fb4ed13181932cc0f4aebe3", debug=True)
    # m.run()

    # Detect Virtualization Environment via Win32_ComputerSystem value(Windows)
    # m = WindowsModule("6249bc4e414705609848bacb")
    # m.run()

    # Detect Virtualization Environment via Current Tempature value(Windows)
    # m = WindowsModule("6249bc4e414705609848bac4")
    # m.run()

    # SYSTEM NETWORK CONFIGURATION DISCOVERY
    # m = WindowsModule("5fb4ec77181932cc0f4adb7b")
    # m.run()

    # SYSTEM OWNER/USER DISCOVERY
    # m = WindowsModule("5fb4ec76181932cc0f4adacc")
    # m.run()

    # REMOTE SYSTEM DISCOVERY (PING SWEEP)
    # Todo: Fix output parser
    # m = WindowsModule("5fb4ec78181932cc0f4adb90")
    # m.run()

    # File and Directory Discovery (cmd.exe)
    # m = WindowsModule("5fb4ec7c181932cc0f4ade74")
    # m.run()

    # Zip a Folder or a File with PowerShell
    # m = WindowsModule("623058ea74200bacb7b7a94c")
    # m.run()

    # Encoding & Exfiltration over DNS
    m = WindowsModule("60f4617c5d2974b7fdd335a8")
    m.run()
