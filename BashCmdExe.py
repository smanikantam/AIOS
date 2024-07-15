import json
import subprocess
from typing import List, Dict, Union

class BashCommandExecutor:
    def __init__(self):
        self.commands: List[str] = []
        self.outputs: List[str] = []

    def load_commands_from_json(self, json_input: str) -> None:
        """
        Load commands from a JSON string.
        """
        try:
            data: Dict[str, List[str]] = json.loads(json_input)
            self.commands = data.get("commands", [])
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    def execute_commands(self, json_input: str = None) -> str:
        """
        Execute all loaded commands and store their outputs.
        If json_input is provided, load commands from it first.
        """
        if json_input:
            self.load_commands_from_json(json_input)

        if not self.commands:
            raise ValueError("No commands loaded")

        self.outputs = []
        for cmd in self.commands:
            try:
                result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
                self.outputs.append(f"Command '{cmd}' output:\n{result.stdout}")
            except subprocess.CalledProcessError as e:
                self.outputs.append(f"Command '{cmd}' failed with error:\n{e.stderr}")
            except Exception as e:
                self.outputs.append(f"Error executing '{cmd}': {str(e)}")

        return self.get_output()

    def get_output(self) -> str:
        """
        Get the combined output of all executed commands.
        """
        return "\n\n".join(self.outputs)

# The main() function and if __name__ == "__main__": block can be removed
# as they're not needed for the integration with main.py