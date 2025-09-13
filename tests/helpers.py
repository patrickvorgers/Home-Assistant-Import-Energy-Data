import filecmp
import glob
import inspect
import shutil
import subprocess
import sys
import tempfile
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
    Execute scripts, compare their CSV outputs against samples, and clean up.

    Args:
        repo_root: Path to project root.
        commands: List of tuples (script_filename, [args]).
        sample_dirname: Name of the directory containing sample CSVs.

    Workflow:
      1. Determine the source directory from the calling test's location.
      2. For each command:
         a. Copy required input files to a temporary directory.
         b. Execute the script using the temporary input path.
         c. Compare any generated CSVs in the temporary directory with
            the samples.
    """
    # 1) Locate source directory from test file
    test_file = Path(inspect.stack()[1].filename).resolve()
    source_dir = test_file.parent.parent
    assert source_dir.exists(), f"Source directory not found: {source_dir}"

    # 2) Process each command individually
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

        # Determine input path (first non-option argument)
        input_idx = next(
            (i for i, val in enumerate(expanded) if not val.startswith("-")),
            None,
        )
        assert input_idx is not None, "No input file specified"
        input_pattern = expanded[input_idx]
        pattern_path = Path(input_pattern)
        if not pattern_path.is_absolute():
            pattern_path = source_dir / pattern_path
        input_paths = glob.glob(str(pattern_path))
        assert input_paths, f"No input files found for pattern: {input_pattern}"
        input_dir = Path(input_paths[0]).parent

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Copy input files to temporary directory
            for path in input_paths:
                shutil.copy(path, tmp_path / Path(path).name)

            # Replace input parameter to point to temp directory
            expanded[input_idx] = str(tmp_path / Path(input_pattern).name)

            # Snapshot before
            before = {f.name for f in tmp_path.glob("*.csv")}

            # Run the script
            run_script(script_path, cwd=source_dir, params=expanded)

            # Determine new files
            after = {f.name for f in tmp_path.glob("*.csv")}
            new_files = after - before
            # Filter out empty files which indicate no applicable data
            meaningful = [
                name
                for name in new_files
                if (tmp_path / name).stat().st_size > 0
            ]
            assert meaningful, "No new CSV files were generated."

            # Compare against samples in original input directory
            sample_dir = input_dir
            for name in sorted(meaningful):
                generated = tmp_path / name
                sample = sample_dir / name
                assert sample.exists(), f"Sample missing for {name}: {sample}"
                assert filecmp.cmp(
                    generated, sample, shallow=False
                ), f"Generated CSV '{name}' does not match sample"
