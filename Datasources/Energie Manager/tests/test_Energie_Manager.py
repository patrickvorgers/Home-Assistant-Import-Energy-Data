from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "EnergieManagerDataPrepare.py",
        ["-y", "Sample files/*.csv"],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
