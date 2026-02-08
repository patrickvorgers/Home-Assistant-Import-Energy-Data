from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("EDCCRDataPrepare.py", ["-y", "Sample files/sample_solar_data.csv"]),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
