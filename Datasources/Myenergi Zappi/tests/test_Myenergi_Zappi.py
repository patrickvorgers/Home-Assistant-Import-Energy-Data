from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "MyenergiZappiDataPrepare.py",
        ["-y", "Sample files/XXXXXXXX_zappi_report.csv"],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
