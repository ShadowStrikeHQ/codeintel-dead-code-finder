# codeintel-Dead-Code-Finder
Identifies and reports potentially unused code blocks or variables within a project. Useful for code cleanup and reducing attack surface. - Focused on Tools for static code analysis, vulnerability scanning, and code quality assurance

## Install
`git clone https://github.com/ShadowStrikeHQ/codeintel-dead-code-finder`

## Usage
`./codeintel-dead-code-finder [params]`

## Parameters
- `-h`: Show help message and exit
- `--dependencies`: List of dependencies to use for dead code analysis. Options: flake8, pylint, pyre-check.
- `--output_file`: Path to save the results to a file. If not provided, results are printed to the console.
- `--ignore`: No description provided

## License
Copyright (c) ShadowStrikeHQ
