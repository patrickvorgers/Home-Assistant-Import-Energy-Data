from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS = [
    (
        "MeterNDataPrepare.py",
        [
            "-y",
            "Sample files/7Prelievi20??.csv",
            "elec_feed_in_tariff_1_high_resolution.csv",
        ],
    ),
    (
        "MeterNDataPrepare.py",
        [
            "-y",
            "Sample files/8Immissioni20??.csv",
            "elec_feed_out_tariff_1_high_resolution.csv",
        ],
    ),
    (
        "MeterNDataPrepare.py",
        [
            "-y",
            "Sample files/1FV_Totale20??.csv",
            "elec_solar_high_resolution.csv",
        ],
    ),
]


def test_commands(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS)
