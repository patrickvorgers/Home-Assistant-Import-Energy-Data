import filecmp
import inspect
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def run_script(
    script_path: Path, cwd: Path, params: Optional[List[str]] = None
) -> None:
    """
    Execute the given Python script with optional parameters and assert it exits successfully.

    Args:
        script_path: Full path to the script to run.
        cwd: Working directory for script execution.
        params: List of command-line arguments (optional).

    Raises:
        AssertionError if the script exits with a non-zero status.
    """
    cmd = [sys.executable, str(script_path)]
    if params is None:
        params = []
    if params:
        cmd.extend(params)
    result = subprocess.run(cmd, cwd=cwd)
    assert (
        result.returncode == 0
    ), f"Script {script_path} exited with {result.returncode}"


def run_commands(
    repo_root: Path,
    commands: List[Tuple[str, List[str]]],
    sample_dirname: str = "Sample files",
) -> None:
    """
    Execute all scripts first, then compare any CSV outputs against samples and clean up.

    Args:
        repo_root: Path to project root.
        commands: List of tuples (script_filename, [args]).
        sample_dirname: Name of the directory containing sample CSVs.

    Workflow:
      1. Determine the source directory from the calling test's location.
      2. Snapshot existing '*.csv' files once before running any scripts.
      3. Execute all scripts in sequence with their parameters.
      4. Snapshot '*.csv' files after all scripts have run and identify new files.
      5. For each new CSV: check existence of matching sample and content equality.
      6. Delete each new CSV.
    """
    # 1) Locate source directory from test file
    test_file = Path(inspect.stack()[1].filename).resolve()
    source_dir = test_file.parent.parent
    assert source_dir.exists(), f"Source directory not found: {source_dir}"

    # 2) Snapshot before
    before = {f.name for f in source_dir.glob("*.csv")}

    # 3) Run all commands
    for script_name, params in commands:
        script_path = source_dir / script_name
        assert script_path.exists(), f"Script not found: {script_path}"

        # Expand any path-like args relative to source_dir
        expanded: List[str] = []
        for p in params or []:
            p_path = Path(p)
            candidate = source_dir / p_path
            if p_path.parent != Path(".") and candidate.exists():
                expanded.append(str(candidate))
            else:
                expanded.append(p)
        run_script(script_path, cwd=source_dir, params=expanded)

    # 4) Snapshot after and determine new files
    after = {f.name for f in source_dir.glob("*.csv")}
    new_files = after - before
    assert new_files, "No new CSV files were generated."

    # 5) Compare samples
    sample_dir = source_dir / sample_dirname
    assert sample_dir.exists(), f"Sample directory not found: {sample_dir}"

    for name in sorted(new_files):
        generated = source_dir / name
        sample = sample_dir / name
        assert sample.exists(), f"Sample missing for {name}: {sample}"
        assert filecmp.cmp(
            generated, sample, shallow=False
        ), f"Generated CSV '{name}' does not match sample"

    # 6) Cleanup generated CSVs
    for name in new_files:
        (source_dir / name).unlink()
