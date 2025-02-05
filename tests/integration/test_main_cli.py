from pathlib import Path
from .common import verify_cli_command, ExitCode, PIXI_VERSION
import pytest


def test_pixi(pixi: Path) -> None:
    verify_cli_command(
        [pixi], ExitCode.INCORRECT_USAGE, stdout_excludes=f"[version {PIXI_VERSION}]"
    )
    verify_cli_command([pixi, "--version"], ExitCode.SUCCESS, stdout_contains=PIXI_VERSION)


@pytest.mark.slow
def test_project_commands(pixi: Path, tmp_path: Path) -> None:
    manifest_path = tmp_path / "pixi.toml"
    # Create a new project
    verify_cli_command([pixi, "init", tmp_path], ExitCode.SUCCESS)

    # Channel commands
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "channel",
            "add",
            "bioconda",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "channel", "list"],
        ExitCode.SUCCESS,
        stdout_contains="bioconda",
    )
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "channel",
            "remove",
            "bioconda",
        ],
        ExitCode.SUCCESS,
    )

    # Description commands
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "description",
            "set",
            "blabla",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "description", "get"],
        ExitCode.SUCCESS,
        stdout_contains="blabla",
    )

    # Environment commands
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "environment",
            "add",
            "test",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "environment", "list"],
        ExitCode.SUCCESS,
        stdout_contains="test",
    )
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "environment",
            "remove",
            "test",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "environment", "list"],
        ExitCode.SUCCESS,
        stdout_excludes="test",
    )

    # Platform commands
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "platform",
            "add",
            "linux-64",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "platform", "list"],
        ExitCode.SUCCESS,
        stdout_contains="linux-64",
    )
    verify_cli_command(
        [
            pixi,
            "project",
            "--manifest-path",
            manifest_path,
            "platform",
            "remove",
            "linux-64",
        ],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "platform", "list"],
        ExitCode.SUCCESS,
        stdout_excludes="linux-64",
    )

    # Version commands
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "version", "set", "1.2.3"],
        ExitCode.SUCCESS,
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "version", "get"],
        ExitCode.SUCCESS,
        stdout_contains="1.2.3",
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "version", "major"],
        ExitCode.SUCCESS,
        stderr_contains="2.2.3",
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "version", "minor"],
        ExitCode.SUCCESS,
        stderr_contains="2.3.3",
    )
    verify_cli_command(
        [pixi, "project", "--manifest-path", manifest_path, "version", "patch"],
        ExitCode.SUCCESS,
        stderr_contains="2.3.4",
    )


@pytest.mark.slow
def test_search(pixi: Path) -> None:
    verify_cli_command(
        [pixi, "search", "rattler-build", "-c", "conda-forge"],
        ExitCode.SUCCESS,
        stdout_contains="rattler-build",
    )
    verify_cli_command(
        [pixi, "search", "rattler-build", "-c", "https://fast.prefix.dev/conda-forge"],
        ExitCode.SUCCESS,
        stdout_contains="rattler-build",
    )


@pytest.mark.slow
def test_simple_project_setup(pixi: Path, tmp_path: Path) -> None:
    manifest_path = tmp_path / "pixi.toml"
    conda_forge = "https://fast.prefix.dev/conda-forge"
    # Create a new project
    verify_cli_command([pixi, "init", "-c", conda_forge, tmp_path], ExitCode.SUCCESS)

    # Add package
    verify_cli_command(
        [pixi, "add", "--manifest-path", manifest_path, "_r-mutex"],
        ExitCode.SUCCESS,
        stderr_contains="Added",
    )
    verify_cli_command(
        [
            pixi,
            "add",
            "--manifest-path",
            manifest_path,
            "--feature",
            "test",
            "_r-mutex==1.0.1",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["test", "==1.0.1"],
    )
    verify_cli_command(
        [
            pixi,
            "add",
            "--manifest-path",
            manifest_path,
            "--platform",
            "linux-64",
            f"{conda_forge}::_r-mutex",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["linux-64", "conda-forge"],
    )
    verify_cli_command(
        [
            pixi,
            "add",
            "--manifest-path",
            manifest_path,
            "-f",
            "test",
            "-p",
            "osx-arm64",
            "_r-mutex",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["osx-arm64", "test"],
    )

    # Remove package
    verify_cli_command(
        [pixi, "remove", "--manifest-path", manifest_path, "_r-mutex"],
        ExitCode.SUCCESS,
        stderr_contains="Removed",
    )
    verify_cli_command(
        [
            pixi,
            "remove",
            "--manifest-path",
            manifest_path,
            "--feature",
            "test",
            "_r-mutex",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["test", "Removed"],
    )
    verify_cli_command(
        [
            pixi,
            "remove",
            "--manifest-path",
            manifest_path,
            "--platform",
            "linux-64",
            f"{conda_forge}::_r-mutex",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["linux-64", "conda-forge", "Removed"],
    )
    verify_cli_command(
        [
            pixi,
            "remove",
            "--manifest-path",
            manifest_path,
            "-f",
            "test",
            "-p",
            "osx-arm64",
            "_r-mutex",
        ],
        ExitCode.SUCCESS,
        stderr_contains=["osx-arm64", "test", "Removed"],
    )


@pytest.mark.slow
def test_pixi_init_pyproject(pixi: Path, tmp_path: Path) -> None:
    manifest_path = tmp_path / "pyproject.toml"
    # Create a new project
    verify_cli_command([pixi, "init", tmp_path, "--format", "pyproject"], ExitCode.SUCCESS)
    # Verify that install works
    verify_cli_command([pixi, "install", "--manifest-path", manifest_path], ExitCode.SUCCESS)
