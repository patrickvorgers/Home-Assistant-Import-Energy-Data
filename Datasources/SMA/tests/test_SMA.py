from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "SMADataPrepare.py",
        [
            "-y",
            "Sample files/SUNNY_TRIPOWER_8.0_XXXXXXXXXX_Daily_2025_07_14_14_36_40.csv",
            "elec_solar_high_resolution.csv",
        ],
    ),
    (
        "SMADataPrepare.py",
        [
            "-y",
            "Sample files/SUNNY_TRIPOWER_8.0_XXXXXXXXXX_5Min_2025_07_14_13_32_21.csv",
            "elec_solar_low_resolution.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
