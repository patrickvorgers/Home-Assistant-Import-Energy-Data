from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    ("AmerenElectricDataPrepare.py", ["-y", "Sample files/ACE_Electric_72621898_03_30_2024_03_30_2025.csv"]),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
