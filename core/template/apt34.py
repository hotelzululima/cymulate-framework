"""
Advanced Scenario - APT 34 (OilRig)
"""
from core.module.windows import WindowsModule


PROFILE = {
    "62385f03a0e69ed2274622cc": {},
    "628263ae9bad2dfa4b66d4c6": {},
    "60f43effac529a1c1f25ebdc": {},
    "6249bc4d414705609848bab6": {},
    "5fb4ec71181932cc0f4ad6cf": {},
    "5fb4ed13181932cc0f4aebe3": {},
    "6249bc4e414705609848bacb": {},
    "6249bc4e414705609848bac4": {},
    "5fb4ec77181932cc0f4adb7b": {},
    "5fb4ec76181932cc0f4adacc": {},
    "5fb4ec78181932cc0f4adb90": {},
    "5fb4ec7c181932cc0f4ade74": {},
    "623058ea74200bacb7b7a94c": {},
    "60f4617c5d2974b7fdd335a8": {}
}


def start():
    for module_id, args in PROFILE.items():
        m = WindowsModule(module_id, log_level="SUCCESS")
        m.input_arguments = args
        m.run()
