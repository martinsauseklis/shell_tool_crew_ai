import subprocess
import os
from typing import Type, Optional
from pydantic import BaseModel
from crewai.tools import BaseTool


class ShellCommandToolInput(BaseModel):
    """Input schema for the ShellCommandTool."""
    command: str
    directory: Optional[str] = "."


class ShellCommandTool(BaseTool):
    name: str = "Shell Command Tool"
    description: str = (
        "Executes CMD commands inside a specified folder. "
        "If the folder does not exist, it will be created automatically. "
        "Useful for installing dependencies, running scripts, and automating development tasks."
    )
    args_schema: Type[BaseModel] = ShellCommandToolInput

    def _run(self, command: str, directory: Optional[str] = ".") -> str:
        """Runs a CMD command in a given directory, creating it if needed."""
        try:
            # Validate command
            if not command or not command.strip():
                return "Error: Command cannot be empty"

            # Use current directory if not specified
            if not directory:
                directory = "."

            # Resolve to absolute path
            directory = os.path.abspath(directory)

            # Create directory if missing
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)

            result = subprocess.run(
                ["cmd", "/c", command],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout to prevent hanging
            )

            if result.returncode == 0:
                return (
                    f"Command executed successfully in: {directory}\n"
                    f"Output:\n{result.stdout.strip()}"
                )
            else:
                return (
                    f"Command executed with warnings/errors in: {directory}\n"
                    f"STDOUT:\n{result.stdout.strip()}\n\n"
                    f"STDERR:\n{result.stderr.strip()}"
                )

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after 300 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
