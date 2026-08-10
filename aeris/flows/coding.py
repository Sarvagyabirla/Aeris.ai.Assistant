from aeris.flows.base import BaseFlow


class CodingFlow(BaseFlow):
    """Specialized flow for software development and coding tasks."""

    def get_flow_system_instruction(self) -> str:
        return (
            "You are operating in the Coding Flow. "
            "Focus on writing clean, modular, and well-documented code. "
            "Always consider edge cases, error handling, and performance. "
            "When writing files, use the file system tools carefully. "
            "If requested to run code, use the command execution tool and report any errors."
        )

    def get_flow_tools(self) -> list:
        # For coding, we primarily want filesystem and command tools.
        return ["fs_control", "command_execution"]
