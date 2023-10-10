from __future__ import annotations


class ExecutableInitParams:
    def __init__(
        self, name: str, command_line_argument: str, environment_variable: str, default_relative_path: str
    ) -> None:
        self.name = name
        self.path = f"{self.name}_path"
        self.argument = command_line_argument
        self.environment_variable = environment_variable
        self.default_relative_path = default_relative_path
