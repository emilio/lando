import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo_seed() -> Path:
    """
    Return the path to a patch to set up a base git repo for tests.

    The diff can  apply on an empty repo to create a known base for application
    of other patches as part of the tests.
    """
    return Path(__file__).parent / "data"


@pytest.fixture
def git_repo(tmp_path: Path, git_repo_seed: Path) -> Path:
    """
    Creates a temporary Git repository for testing purposes.

    Args:
        tmp_path (pathlib.Path): The base temporary directory path (pytest fixture)

    Returns:
        pathlib.Path: The path to the created Git repository.
    """
    repo_dir = tmp_path / "git_repo"
    subprocess.run(["git", "init", repo_dir], check=True)
    subprocess.run(["git", "branch", "-m", "main"], check=True, cwd=repo_dir)
    _git_setup_user(repo_dir)
    _git_ignore_denyCurrentBranch(repo_dir)
    for patch in sorted(git_repo_seed.glob("*")):
        subprocess.run(["git", "am", str(patch)], check=True, cwd=repo_dir)

    # Create a separate base branch for branch tests.
    _run_commands(
        [
            ["git", "checkout", "-b", "dev"],
            ["git", "commit", "--allow-empty", "-m", "dev"],
            ["git", "checkout", "main"],
        ],
        repo_dir,
    )
    return repo_dir


@pytest.fixture
def git_setup_user():
    return _git_setup_user


def _git_setup_user(repo_dir: Path):
    """Configure the git user locally to repo_dir so as not to mess with the real user's configuration."""
    _run_commands(
        [
            ["git", "config", "user.name", "Py Test"],
            ["git", "config", "user.email", "pytest@lando.example.net"],
        ],
        repo_dir,
    )


def _run_commands(commands: list[list[str]], cwd: Path):
    for c in commands:
        subprocess.run(c, check=True, cwd=cwd)


def _git_ignore_denyCurrentBranch(repo_dir: Path):
    """Disable error when pushing to this non-bare repo.

    This is a sane protection in general, but it gets in the way of the tests here,
    where we just want a target, and don't care much about the final state of this
    target after everything is done.
    """
    subprocess.run(
        ["git", "config", "receive.denyCurrentBranch", "ignore"],
        check=True,
        cwd=repo_dir,
    )
