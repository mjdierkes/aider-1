from .auto_prompts import AutoPrompts
from .editblock_coder import EditBlockCoder
from aider.io import InputOutput
from aider.run_cmd import run_cmd


class AutoCoder(EditBlockCoder):
    # Enable all autonomous behaviors
    suggest_shell_commands = True  # Allow suggesting and running shell commands
    auto_commits = True  # Automatically commit changes
    dirty_commits = True  # Allow committing dirty files before edits
    auto_lint = True  # Automatically run linting
    auto_test = True  # Automatically run tests
    detect_urls = True  # Automatically detect and process URLs
    auto_copy_context = True  # Automatically copy context when needed
    max_reflections = 10  # Allow more reflections for autonomous operation

    edit_format = "auto"
    gpt_prompts = AutoPrompts()

    def __init__(self, *args, **kwargs):
        # Override kwargs to force autonomous settings
        kwargs.update({
            'auto_commits': True,
            'dirty_commits': True,
            'auto_lint': True,
            'suggest_shell_commands': True,
        })
        super().__init__(*args, **kwargs)

        # Override self.io.confirm_ask so that it always returns True.
        # This ensures all commands auto-approve.
        def always_approve(*_args, **_kwargs):
            return True
        self.io.confirm_ask = always_approve

    def handle_shell_commands(self, commands_str, group):
        commands = commands_str.strip().splitlines()
        accumulated_output = ""
        for command in commands:
            command = command.strip()
            if not command or command.startswith("#"):
                continue

            self.io.tool_output()
            self.io.tool_output(f"Running {command}")
            # Add the command to input history
            self.io.add_to_input_history(f"/run {command.strip()}")
            exit_status, output = run_cmd(command, error_print=self.io.tool_error, cwd=self.root)
            if output:
                accumulated_output += f"Output from {command}\n{output}\n"

        if accumulated_output.strip():
            num_lines = len(accumulated_output.strip().splitlines())
            line_plural = "line" if num_lines == 1 else "lines"
            self.io.tool_output(f"Added {num_lines} {line_plural} of output to the chat.")
            # Only trigger reflection if there was an error (non-zero exit status)
            if exit_status != 0:
                self.reflected_message = accumulated_output
            return accumulated_output


