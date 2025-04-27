#!/usr/bin/env python3
import sys
import subprocess
import filecmp
from pathlib import Path

# === Configuration ===
TEST_SUBFOLDER = "test"
TEST_DRIVER    = "test.py"
SAMPLE_DIRNAME = "Sample files"

def main():
    # Always use the folder this script lives in as the root
    root = Path(__file__).resolve().parent
    overall_failed = False

    print("Running tests in all subdirectories (alphabetical order)...\n")

    # Only immediate child directories
    for subdir in sorted(p for p in root.iterdir() if p.is_dir()):
        test_script = subdir / TEST_SUBFOLDER / TEST_DRIVER
        sample_dir  = subdir / SAMPLE_DIRNAME

        if not test_script.exists():
            print(f"Skipping {subdir.name} (no {TEST_SUBFOLDER}/{TEST_DRIVER})")
            continue

        print(f"\n===== Testing {subdir.name} =====")
        # 1) Snapshot CSVs before
        before = {f.name for f in subdir.glob("*.csv")}

        # 2) Run test.py, blocking until completion
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=subdir
        )
        if result.returncode != 0:
            print(f"ERROR: {TEST_SUBFOLDER}/{TEST_DRIVER} in {subdir.name} FAILED (exit code {result.returncode})")
            overall_failed = True
        else:
            # 3) Compare any generated CSVs against Sample files
            for csv_file in subdir.glob("*.csv"):
                sample = sample_dir / csv_file.name
                if not sample.exists():
                    print(f"ERROR: Sample file '{SAMPLE_DIRNAME}/{csv_file.name}' not found")
                    overall_failed = True
                else:
                    match = filecmp.cmp(csv_file, sample, shallow=False)
                    if match:
                        print(f"OK:    {csv_file.name} matches sample")
                    else:
                        print(f"ERROR: {csv_file.name} FAILED to match sample")
                        overall_failed = True

        # 4) Cleanup only the newly created CSVs
        after = {f.name for f in subdir.glob("*.csv")}
        new_files = after - before
        if new_files:
            print("Cleaning up generated CSV files:")
            for name in sorted(new_files):
                try:
                    (subdir / name).unlink()
                    print(f"  Deleted {name}")
                except Exception as e:
                    print(f"  Failed to delete {name}: {e}")

    print()
    if overall_failed:
        print("Some tests FAILED.")
        sys.exit(1)
    else:
        print("All tests passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
