# cymulate-framework

* **Notice**: This project is still in development and not ready for production use.

## Introduction

A framework to automate Cymulate's modules and templates.

It's based On the [Cymualte](https://cymulate.com/) BAS (Break and Attack Simulation) platform.

This project is aimed to help security professionals construct fully customizable and automated APT attacks easily.

## Functionality

- [ ] Scrape modules and templates from Cymulate's website and transform them to scripts.
- [ ] Automate the execution of templates such as APT, Phishing, etc.

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
- `ClI` - A CLI to interact with the framework.

## Contributing

Feel free to submit pull requests and issues.

## License

[MIT](https://choosealicense.com/licenses/mit/)
