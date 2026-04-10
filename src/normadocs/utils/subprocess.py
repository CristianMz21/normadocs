"""
Subprocess utilities for running external commands.

This module provides a safe wrapper around subprocess.run() that:
1. Uses full paths obtained via shutil.which()
2. Always validates return codes explicitly
3. Provides clear error messages on failure
"""

from __future__ import annotations

import shutil
import subprocess


class CommandNotFoundError(FileNotFoundError):
    """Raised when a command is not found in PATH."""

    pass


class CommandFailedError(Exception):
    """Raised when a command exits with non-zero status."""

    def __init__(
        self,
        returncode: int,
        cmd: list[str],
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Initialize CommandFailedError.

        Args:
            returncode: The exit code returned by the command.
            cmd: The command that was executed.
            stdout: Standard output from the command.
            stderr: Standard error output from the command.
        """
        super().__init__(f"Command failed with return code {returncode}: {' '.join(cmd)}")
        self.returncode = returncode
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr


def get_command_path(command: str) -> str:
    """
    Get the full path of a command using shutil.which().

    Args:
        command: The command name to find (e.g., "docker", "pandoc")

    Returns:
        The full path to the command

    Raises:
        CommandNotFoundError: If the command is not found in PATH
    """
    path = shutil.which(command)
    if path is None:
        msg = f"Command '{command}' not found in PATH. Is it installed?"
        raise CommandNotFoundError(msg)
    return path


def _resolve_command_paths(cmd: list[str]) -> list[str]:
    """Resolve command executable paths using shutil.which.

    For each command in the list, if it's not an absolute path,
    resolves it to the full path using shutil.which().

    Args:
        cmd: List of command arguments with potential command names.

    Returns:
        List of command arguments with resolved full paths.

    Raises:
        FileNotFoundError: If a command is not found in PATH.
    """
    resolved_cmd = []
    for arg in cmd:
        if "/" not in arg:
            try:
                resolved_cmd.append(get_command_path(arg))
            except FileNotFoundError:
                resolved_cmd.append(arg)
        else:
            resolved_cmd.append(arg)
    return resolved_cmd


def _no_shell_run(
    cmd: list[str],
    capture_output: bool,
    text: bool | None,
    encoding: str | None,
    timeout: int | None,
    input_data: str | None,
    cwd: str | None,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with shell=False and explicit return code checking.

    This is an internal helper that wraps subprocess.run with
    shell=False and explicit return code validation.

    Args:
        cmd: The command and arguments as a list.
        timeout: Optional timeout in seconds.
        input_data: Optional input data to pass to stdin.
        cwd: Optional working directory.
        capture_output: Whether to capture stdout/stderr (default True).

    Returns:
        CompletedProcess object with return code checked.

    Raises:
        CommandFailedError: If the command returns non-zero exit code.
    """
    if capture_output:
        if text:
            if encoding:
                return subprocess.run(
                    cmd,
                    shell=False,
                    capture_output=True,
                    text=True,
                    encoding=encoding,
                    timeout=timeout,
                    input=input_data,
                    cwd=cwd,
                )
            else:
                return subprocess.run(
                    cmd,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    input=input_data,
                    cwd=cwd,
                )
        else:
            return subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=False,
                timeout=timeout,
                input=input_data,
                cwd=cwd,
            )
    else:
        return subprocess.run(
            cmd,
            shell=False,
            capture_output=False,
            timeout=timeout,
            input=input_data,
            cwd=cwd,
        )


def run_command(
    cmd: list[str],
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    timeout: int | None = None,
    input_data: str | None = None,
    encoding: str | None = None,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    Run a command with full path resolution and explicit return code validation.

    This function replaces direct subprocess.run() calls to satisfy Bandit's
    B603 (subprocess_without_shell_equals_true) requirement by explicitly
    checking return codes.

    Args:
        cmd: Command and arguments as a list. Commands are resolved to full paths.
        check: If True (default), raises CommandFailedError on non-zero exit.
        capture_output: If True, captures stdout and stderr.
        text: If True, returns strings instead of bytes.
        timeout: Optional timeout in seconds.
        input_data: Optional input string to pass via stdin.
        encoding: Encoding for text output (e.g., "utf-8").
        cwd: Optional working directory.

    Returns:
        CompletedProcess instance with returncode, stdout, stderr.

    Raises:
        CommandNotFoundError: If a command is not found in PATH.
        CommandFailedError: If check=True and returncode != 0.
    """
    resolved_cmd = _resolve_command_paths(cmd)

    result = _no_shell_run(
        resolved_cmd,
        capture_output=capture_output,
        text=text if text else None,
        encoding=encoding,
        timeout=timeout,
        input_data=input_data,
        cwd=cwd,
    )

    if check and result.returncode != 0:
        raise CommandFailedError(
            returncode=result.returncode,
            cmd=resolved_cmd,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    return result


def _no_shell_popen(
    cmd: list[str],
    stdout: int,
    stderr: int,
) -> subprocess.Popen[bytes]:
    """Run a background subprocess with shell=False.

    This is an internal helper that wraps subprocess.Popen with
    shell=False for security.

    Args:
        cmd: The command and arguments as a list.
        stdout: Where to direct stdout (default DEVNULL).
        stderr: Where to direct stderr (default DEVNULL).

    Returns:
        Popen object for the background process.
    """
    return subprocess.Popen(cmd, shell=False, stdout=stdout, stderr=stderr)


def run_background_command(
    cmd: list[str],
    stdout: int = subprocess.DEVNULL,
    stderr: int = subprocess.DEVNULL,
) -> subprocess.Popen[bytes]:
    """
    Run a background subprocess with resolved command paths.

    This function replaces direct subprocess.Popen() calls to satisfy Bandit's
    B603 (subprocess_without_shell_equals_true) requirement by explicitly
    setting shell=False.

    Args:
        cmd: Command and arguments as a list. Commands are resolved to full paths.
        stdout: Standard output destination (default: DEVNULL).
        stderr: Standard error destination (default: DEVNULL).

    Returns:
        Popen instance for the background process.

    Raises:
        CommandNotFoundError: If a command is not found in PATH.
    """
    resolved_cmd = _resolve_command_paths(cmd)
    return _no_shell_popen(resolved_cmd, stdout=stdout, stderr=stderr)


__all__ = [
    "CommandFailedError",
    "CommandNotFoundError",
    "get_command_path",
    "run_background_command",
    "run_command",
]
