from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "UnitedPowerDataPrepare.py",
        ["-y", "Sample files/united_power_daily_sample.csv"],
    ),
    (
        "UnitedPowerDataPrepare.py",
        ["-y", "Sample files/united_power_hourly_sample.csv"],
    ),
    (
        "UnitedPowerDataPrepare.py",
        ["-y", "Sample files/green_button_data_1760853600000.zip"],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    Tests daily and hourly granularity, plus Green Button XML format (ZIP).
    """
    run_commands(repo_root, COMMANDS)
