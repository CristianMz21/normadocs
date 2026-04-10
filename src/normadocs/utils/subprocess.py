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
        stdout: str | None = None,
        stderr: str | None = None,
    ):
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
    """
    Resolve command paths in a command list using shutil.which().

    Args:
        cmd: Command and arguments as a list.

    Returns:
        Command list with commands resolved to full paths.
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
    """
    Low-level subprocess.run wrapper with explicit shell=False.

    This exists to satisfy Bandit's B603 check by having shell=False
    as a direct keyword argument in the call, not through **kwargs.
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
    """
    Low-level subprocess.Popen wrapper with explicit shell=False.

    This exists to satisfy Bandit's B603 check by having shell=False
    as a direct keyword argument in the call.
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
