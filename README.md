# cymulate-framework

- **Notice**: This project is still under development and not ready for production use.

## Introduction

![](https://i.imgur.com/f1LLGB6.png)

A framework to automate Cymulate's modules and templates.

It's based On the [Cymualte](https://cymulate.com/) BAS (Break and Attack Simulation) platform.

This project is aimed to help security professionals construct fully customizable and automated APT attacks easily.

## Functionality

- [ ] Scrape modules and templates from Cymulate and transform them into scripts.
- [ ] Automate the execution of templates such as APT, Phishing, etc.
- [ ] Generate standalone EXE for templates and bypass AMSI, Antivirus

## Environment

- Python 3.11+
- Poetry (`pip install poetry`)

## Development

### Setup

```powershell
poetry install
poetry shell
```

### Blueprint

- `Basic structure` - The basic structure of the project.
- `APT template` - APT template automation test.
- `Scrape modules and templates` - Scrape modules and templates via Cymulate's [API](https://api.app.cymulate.com/docs/#/)
- `Transform modules and templates` - Transform modules and templates into cymulate-framework modules.
- `Automate execution` - Automate the execution of templates.
- `APT Script generator` - Generate scripts for APT template with extracted specific execution scripts (don't wanna load the 20+mb json file) and load corresponding required 3rd party pip packages into scripts
- `Pack Script to EXE` - Pack generated template script with its requirements(pip packages, execution scripts) into EXE via `pyisntaller`, `py2exe` or `Nuitka`
- `ClI` - A CLI to interact with the framework.

## Contributing

Feel free to submit pull requests and issues.

## License

[MIT](https://choosealicense.com/licenses/mit/)
