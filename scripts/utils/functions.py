import requests
import subprocess

from rich import print as rich_print
from rich.panel import Panel


def get_latest_commit_api(owner: str, repository: str, branch: str):
    """
    Get the latest commit hash of the given repository and branch.

    Args:
        owner (str): The owner of the repository.
        repository (str): The name of the repository.
        branch (str): The name of the branch.

    Returns:
        str: The latest commit hash.
    """
    url = f"https://api.github.com/repos/{owner}/{repository}/git/refs/heads/{branch}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(response.status_code)
        sys.exit(1)
    
    data = response.json()
    return data["object"]["sha"]


def get_latest_commit_local(directory: str = None):
    """
    Get the latest commit hash of the given directory.

    Args:
        directory (str): The directory of the git repository.

    Returns:
        str: The latest commit hash.
    """
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=directory,
            text=True,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise e
    return res.stdout.strip()


def print_box(message: str, title: str = None, color: str = "white", expand: bool = True):
    """
    Print a message in a box with a title.
    This uses the rich library to print the message, just like FabSim3 does.

    Args:
        title (str): The title of the box.
        message (str): The message to be printed in the box.
        color (str): The color of the box.
        expand (bool): If True, the box will expand to the width of the terminal.

    Returns:
        None
    """
    rich_print(
        Panel(
            message,
            title=f"[{color}]{title}[/{color}]" if title is not None else None,
            border_style=color,
            expand=expand,
        )
    )