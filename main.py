import argparse
import logging
import os
import subprocess
import sys
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Finds potentially unused code blocks or variables in a Python project.")
    parser.add_argument("project_path", help="Path to the Python project directory.")
    parser.add_argument(
        "--dependencies",
        nargs="+",
        default=["flake8", "pylint", "pyre-check"],
        help="List of dependencies to use for dead code analysis. Options: flake8, pylint, pyre-check.",
    )
    parser.add_argument(
        "--output_file",
        help="Path to save the results to a file. If not provided, results are printed to the console.",
    )
    parser.add_argument(
        "--ignore",
        nargs="+",
        default=[],
        help="List of files or directories to ignore during analysis (relative to project_path).",
    )

    return parser


def run_flake8(project_path, ignore):
    """
    Runs flake8 on the project and returns the output.
    Args:
        project_path (str): Path to the Python project directory.
        ignore (list): List of files or directories to ignore.

    Returns:
        str: The output from flake8.
    """
    try:
        command = ["flake8", project_path]
        if ignore:
            command.extend(["--exclude", ",".join(ignore)])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout

    except FileNotFoundError:
        logging.error("Flake8 is not installed. Please install it using 'pip install flake8'.")
        return ""
    except Exception as e:
        logging.error(f"An error occurred while running flake8: {e}")
        return ""


def run_pylint(project_path, ignore):
    """
    Runs pylint on the project and returns the output.

    Args:
        project_path (str): Path to the Python project directory.
        ignore (list): List of files or directories to ignore.

    Returns:
        str: The output from pylint.
    """
    try:
        command = ["pylint", project_path]
        if ignore:
            ignore_str = ",".join(ignore)
            command.extend(["--ignore", ignore_str])

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout

    except FileNotFoundError:
        logging.error("Pylint is not installed. Please install it using 'pip install pylint'.")
        return ""
    except Exception as e:
        logging.error(f"An error occurred while running pylint: {e}")
        return ""


def run_pyre(project_path, ignore):
    """
    Runs pyre-check on the project and returns the output.

    Args:
        project_path (str): Path to the Python project directory.
        ignore (list): List of files or directories to ignore.

    Returns:
        str: The output from pyre-check.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            pyre_config_path = os.path.join(temp_dir, ".pyre_configuration.local")

            # Create .pyre_configuration.local file with excludes
            with open(pyre_config_path, "w") as f:
                f.write(f"""{{
  "ignore": [{", ".join(map(lambda x: '"' + x + '"', ignore))}],
  "typeshed": null,
  "use_buck": false,
  "source_directories": ["{project_path}"]
}}""")

            command = ["pyre", "check", "--source-directory", project_path, "--configuration", pyre_config_path]

            result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=project_path)
            return result.stdout

    except FileNotFoundError:
        logging.error("Pyre-check is not installed. Please install it using 'pip install pyre-check'.")
        return ""
    except Exception as e:
        logging.error(f"An error occurred while running pyre-check: {e}")
        return ""


def main():
    """
    Main function to execute the dead code finder.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    project_path = args.project_path
    dependencies = args.dependencies
    output_file = args.output_file
    ignore = args.ignore

    # Input validation
    if not os.path.isdir(project_path):
        logging.error(f"Error: '{project_path}' is not a valid directory.")
        sys.exit(1)

    valid_dependencies = ["flake8", "pylint", "pyre-check"]
    for dep in dependencies:
        if dep not in valid_dependencies:
            logging.error(f"Error: '{dep}' is not a valid dependency. Valid options are: {valid_dependencies}")
            sys.exit(1)

    results = {}

    if "flake8" in dependencies:
        logging.info("Running flake8...")
        results["flake8"] = run_flake8(project_path, ignore)
    if "pylint" in dependencies:
        logging.info("Running pylint...")
        results["pylint"] = run_pylint(project_path, ignore)
    if "pyre-check" in dependencies:
        logging.info("Running pyre-check...")
        results["pyre-check"] = run_pyre(project_path, ignore)

    output = ""
    for tool, result in results.items():
        output += f"--- {tool.upper()} ---\n{result}\n\n"

    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(output)
            logging.info(f"Results saved to '{output_file}'")
        except Exception as e:
            logging.error(f"Error writing to file '{output_file}': {e}")
    else:
        print(output)


if __name__ == "__main__":
    main()