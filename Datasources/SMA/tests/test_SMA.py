from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "SMADataPrepare.py",
        [
            "-y",
            "Sample files/SUNNY_TRIPOWER_6.0_XXXXXXXXXX_5Min_2025_07_14_10_08_13.csv",
            "elec_solar_high_resolution.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
