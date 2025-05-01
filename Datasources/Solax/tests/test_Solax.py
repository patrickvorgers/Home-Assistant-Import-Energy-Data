from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("SolaxDataPrepare.py", ["-y", "Sample files/Dummy Site 202?-??.xls"]),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
