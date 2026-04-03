from tests.helpers import run_commands

# List scripts and their CLI args
COMMANDS_API = [
    (
        "EnergieManagerDataPrepare_api.py",
        ["-y", "Sample files/API/export_????.csv"],
    ),
]

COMMANDS_SITE = [
    (
        "EnergieManagerDataPrepare_site.py",
        ["-y", "Sample files/Site/????.csv"],
    ),
]


def test_commands_api(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS_API, r"Sample files/API")


def test_commands_site(repo_root):
    """
    Executes all script commands, then verifies CSV outputs.
    """
    run_commands(repo_root, COMMANDS_SITE, r"Sample files/Site")