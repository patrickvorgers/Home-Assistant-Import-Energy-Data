#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# === CONFIGURE TEST COMMANDS HERE ===
# Each entry is: [python_script, arg1, arg2, ...]
COMMANDS = [
    [
        "iSolarCloudDataPrepare.py",
        "-y",
        "Sample files/Monthly.Report_PLANT_NAME_20241011100248.csv",
    ],
]


def main():
    test_dir = Path(__file__).resolve().parent
    base = test_dir.parent

    for idx, cmd in enumerate(COMMANDS, start=1):
        script_name, *params = cmd
        script_path = base / script_name

        if not script_path.exists():
            print(
                f"[{idx}] ERROR: '{script_name}' not found at {script_path}",
                file=sys.stderr,
            )
            return 1

        full_cmd = [sys.executable, str(script_path)]
        for p in params:
            param_path = Path(p)
            candidate = base / param_path

            # Expand only if it's a path (contains a directory component) and exists
            if param_path.parent != Path(".") and candidate.exists():
                full_cmd.append(str(candidate))
            else:
                full_cmd.append(p)

        print(f"[{idx}] Running: {' '.join(full_cmd)}")
        result = subprocess.run(full_cmd, cwd=base)
        if result.returncode != 0:
            print(
                f"[{idx}] ERROR: '{script_name}' exited with code {result.returncode}",
                file=sys.stderr,
            )
            return 1

        print(f"[{idx}] Success: '{script_name}' completed.\n")

    print("All test commands completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
