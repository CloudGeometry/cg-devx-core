import json
import os
import subprocess
import tempfile
from typing import Tuple, Dict, Any, Optional, List, Generator

from alive_progress import alive_bar

from common.const.common_path import LOCAL_TF_TOOL
from common.logging_config import logger


class TerraformExecutionError(Exception):
    def __init__(self, return_code: int, stdout: str, stderr: str):
        super().__init__(f"Terraform command failed with return code {return_code} and error: \"{stderr}\"")
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


class TfWrapper:
    def __init__(self, working_dir: str = None):
        self.terraform_bin_path = LOCAL_TF_TOOL if os.path.exists(LOCAL_TF_TOOL) else 'terraform'
        self.working_dir = working_dir
        self.tf_command_manager = TerraformCommandManager(self.terraform_bin_path, self.working_dir)
        self.tf_progress_manager = TerraformProgressBar()

    def version(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Executes the Terraform version command and returns the version information.

        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: The version information as a dictionary.
        """
        command = self.tf_command_manager.prepare_terraform_command(
            'version', None, '-json', *args, **kwargs
        )
        logger.info(f"Executing Terraform version with command: {command}")
        return_code, stdout, stderr = self.run_terraform_command(command)
        if return_code != 0:
            raise TerraformExecutionError(return_code, stdout, stderr)
        return json.loads(stdout)

    def init(self, variables: Optional[Dict[str, Any]] = None, *args, **kwargs) -> bool:
        """
        Executes the Terraform init command.

        :param variables: A dictionary of variables to be passed to the command.
        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: True if the command was successful, otherwise raises an exception.
        """
        command = self.tf_command_manager.prepare_terraform_command(
            'init', variables, *args, **kwargs, input=False
        )
        logger.info(f"Executing Terraform init with command: {command}")
        return_code, stdout, stderr = self.run_terraform_command(command)
        if return_code != 0:
            raise TerraformExecutionError(return_code, stdout, stderr)
        return True

    def apply(self, variables: Optional[Dict[str, Any]] = None, *args, **kwargs) -> bool:
        """
        Executes the Terraform apply command with optional variables.

        :param variables: A dictionary of variables to be passed to the command.
        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: True if the command was successful, otherwise raises an exception.
        """
        command = self.tf_command_manager.prepare_terraform_command(
            'apply', variables, '-auto-approve', *args, **kwargs, input=False
        )
        logger.info(f"Executing Terraform apply with command: {command}")
        return_code, stdout, stderr = self.run_terraform_command(command, track_progress=True)
        if return_code != 0:
            logger.error(f"Terraform apply failed with return code {return_code}: {stderr}")
            raise TerraformExecutionError(return_code, stdout, stderr)
        logger.info("Terraform apply executed successfully.")
        return True

    def output(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Executes the Terraform output command and returns the output.

        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: A dictionary containing the output values.
        """
        command = self.tf_command_manager.prepare_terraform_command(
            'output', None, '-json', *args, **kwargs
        )
        logger.info(f"Executing Terraform output with command: {command}")
        return_code, stdout, stderr = self.run_terraform_command(command)
        if return_code != 0:
            raise TerraformExecutionError(return_code, stdout, stderr)

        try:
            json_output = json.loads(stdout)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON output from Terraform.")
            return {}

        result = self._prepare_output(json_output)
        return result

    @staticmethod
    def _prepare_output(tf_output: Optional[dict]) -> Dict[str, Any]:
        """
        Processes the Terraform output JSON and extracts the values.

        :param tf_output: The JSON object representing the Terraform output.
        :return: A dictionary with keys representing the Terraform output variables and their respective values.
        """
        output = {}
        if tf_output:
            for key, value in tf_output.items():
                output[key] = value.get("value", None)
        return output

    def destroy(self, variables: Optional[Dict[str, Any]] = None, *args, **kwargs) -> bool:
        """
        Executes the Terraform destroy command with auto-approve and no input options.

        :param variables: A dictionary of variables to be passed to the command.
        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: True if the command was successful, otherwise raises an exception.
        """
        command = self.tf_command_manager.prepare_terraform_command(
            'destroy', variables, '-auto-approve', *args, **kwargs, input=False
        )
        logger.info(f"Executing Terraform destroy with command: {command}")
        return_code, stdout, stderr = self.run_terraform_command(command, track_progress=True)
        if return_code != 0:
            raise TerraformExecutionError(return_code, stdout, stderr)
        return True

    def run_terraform_command(
            self,
            command: list[str],
            track_progress: bool = False,
    ) -> Tuple[int, str, str]:
        """
        Executes a Terraform command with the option to track its progress. It can use either
        an internal or an external process.

        :param command: The Terraform command and arguments as a list.
        :param track_progress: Flag to indicate whether to track progress.
        :return: Tuple containing the return code of the command, stdout, and stderr.
        """
        process = self.tf_command_manager.execute_terraform_command(command)

        if track_progress:
            self.tf_progress_manager.track_progress(process)
            stdout = self.tf_progress_manager.get_stdout()
        else:
            stdout = list(self.tf_command_manager.generate_output(process))

        return_code, stderr = self.tf_command_manager.get_command_result(process)
        self.tf_command_manager.generate_output()
        return return_code, ''.join(stdout), stderr


class TerraformProgressBar:
    TF_PROGRESS_BAR_TITTLE = "Terraform Progress"

    def __init__(self):
        self.saved_output = []

    @staticmethod
    def parse_plan_output(line: str) -> Tuple[int, int, int]:
        """
        Parses a single line of Terraform output to extract the plan summary.

        :param line: A single line of output from the Terraform process.
        :return: A tuple containing the counts of add, change, and destroy operations if the plan summary is found.
        """
        if "Plan:" in line:
            logger.debug("Plan summary found in output")

            try:
                # Extract the counts of add, change, and destroy operations
                parts = line.split(',')
                add_count = int(parts[0].split()[1])
                change_count = int(parts[1].split()[0])
                destroy_count = int(parts[2].split()[0])
                logger.debug(f"Plan counts - Add: {add_count}, Change: {change_count}, Destroy: {destroy_count}")
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing plan output: {e}")
                return 0, 0, 0

            return add_count, change_count, destroy_count

        return 0, 0, 0

    def _monitor_progress(self, process: subprocess.Popen, total_operations: int):
        """
        Updates the progress bar based on the output of the Terraform process.

        :param process: The running Terraform process.
        :param total_operations: Total number of operations to complete.
        """
        completion_keywords = ["Creation complete", "Modifications complete", "Destruction complete"]

        with alive_bar(total=total_operations, title=self.TF_PROGRESS_BAR_TITTLE) as bar:
            for line in iter(process.stdout.readline, ""):
                self.saved_output.append(line)
                logger.debug(f"Reading line: {line.strip()}")

                if any(keyword in line for keyword in completion_keywords):
                    bar()

    def track_progress(self, process: subprocess.Popen):
        """
        Tracks the progress of a running Terraform process and saves its output.

        :param process: The running Terraform process.
        """
        total_operations = 0

        # Parse the plan output to determine the total number of operations
        for line in iter(process.stdout.readline, ''):
            self.saved_output.append(line)
            logger.debug(f"Reading line during progress tracking: {line.strip()}")

            add, change, destroy = self.parse_plan_output(line)
            total_operations += add + change + destroy

            if total_operations > 0:
                break

        if total_operations > 0:
            self._monitor_progress(process, total_operations)

    def get_stdout(self) -> List[str]:
        """
        Returns the saved stdout lines.

        :return: List of saved stdout lines.
        """
        return self.saved_output


class TerraformCommandManager:
    def __init__(self, terraform_bin_path: str, working_dir: str):
        self.terraform_bin_path = terraform_bin_path
        self.working_dir = working_dir
        self.process = None

    def execute_terraform_command(self, command: list[str]):
        """
        Runs a Terraform command and initializes a process for further reading its output.

        :param command: A list of strings representing the Terraform command and its arguments.
        """
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=self.working_dir
        )
        return self.process

    def generate_output(self, process: Optional[subprocess.Popen] = None) -> Generator[str, None, None]:
        """
        A generator for line-by-line reading of the stdout of a specified or currently running Terraform process.

        This method can work with an external process passed as an argument or use the internal process
        if no external process is provided.

        :param process: Optional; An external subprocess.Popen object to read output from.
                        If not provided, the internal process is used.
        :yield: Each line of output from the Terraform process as a string.
        """
        # Choose the target process (external or internal)
        target_process = process or self.process

        # Iterate through each line of the process's stdout and yield it
        if target_process is not None:
            for line in iter(target_process.stdout.readline, ""):
                yield line

    def get_command_result(self, process: Optional[subprocess.Popen] = None) -> Optional[Tuple[int, str]]:
        """
        Retrieves the result of a Terraform command execution, including the return code and stderr.

        This method can extract the result from an external process passed as an argument or use the internal process
        if no external process is provided.

        :param process: Optional; An external subprocess.Popen object to get results from.
                        If not provided, the internal process is used.
        :return: An optional tuple containing the return code and stderr output of the Terraform process.
        """
        # Choose the target process (external or internal)
        target_process = process or self.process

        # If no valid process is provided or available, return None
        if not target_process:
            return None

        # Communicate with the process to retrieve stderr and the return code
        _, stderr = target_process.communicate()
        return_code = target_process.returncode

        # Reset an internal process if it was used
        if target_process == self.process:
            self.process = None

        # Return the command results
        return return_code, stderr

    @staticmethod
    def _create_var_files(variables: Dict[str, any]) -> str:
        """
        Creates a temporary JSON file with Terraform variables.

        Parameters:
        variables (Dict[str, any]): A dictionary of Terraform variables to be written to the file.

        Returns:
        str: Path to the created temporary file.

        Raises:
        IOError: If there's an error writing to the file.
        """
        # Creating a temporary file with .tfvars.json extension
        try:
            with tempfile.NamedTemporaryFile(mode='w+t', suffix='.tfvars.json', delete=False) as temp_file:
                # Writing the variables in JSON format to the file
                temp_file.write(json.dumps(variables))
                temp_file_path = os.path.abspath(temp_file.name)
                logger.info(f"Temporary Terraform variables file created at: {temp_file_path}")
                return temp_file_path
        except IOError as io_error:
            logger.error(f"Error writing to temporary Terraform variables file: {io_error}")
            # If an error occurs, delete the temporary file and re-raise the exception
            os.unlink(temp_file.name)
            raise

    def prepare_terraform_command(
            self, terraform_command: str, variables: Optional[Dict[str, Any]] = None, *args, **kwargs
    ) -> List[str]:
        """
        Prepares a terraform command with given variables, args, and kwargs.

        :param terraform_command: The terraform command (e.g., 'apply', 'init').
        :param variables: A dictionary of variables to be passed to the command.
        :param args: Additional positional arguments for the command.
        :param kwargs: Additional named arguments for the command.
        :return: A list of command components ready to be executed.
        """
        command = [self.terraform_bin_path, terraform_command]

        if variables:
            var_file_path = self._create_var_files(variables)
            command.append(f'-var-file={var_file_path}')

        for arg in args:
            command.append(str(arg))

        for key, value in kwargs.items():
            value_str = 'true' if value is True else 'false' if value is False else str(value)
            command.append(f'-{key.replace("_", "-")}={value_str}')

        return command
