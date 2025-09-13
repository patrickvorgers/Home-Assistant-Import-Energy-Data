"""Prepare E-REDES export data for Home Assistant import.

The official data export of the Portuguese grid operator E-REDES is an
``.xlsx`` file containing 15‑minute electricity usage values.  This script
parses that spreadsheet without requiring external dependencies such as
``openpyxl`` and converts it into the generic two‑column CSV format used by
the rest of this repository.

The resulting file is named
``elec_feed_in_tariff_1_high_resolution.csv`` and contains rows of
``<unix_timestamp>,<value>`` where the timestamp is localised to
``Europe/Lisbon``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _column_letter(cell_ref: str) -> str:
    """Return the column letter(s) from an Excel cell reference.

    Examples:
        >>> _column_letter("A1")
        'A'
        >>> _column_letter("BC12")
        'BC'
    """

    return re.match(r"[A-Z]+", cell_ref).group(0)  # type: ignore[arg-type]


def _parse_shared_strings(z: ZipFile) -> List[str]:
    """Extract the shared string table from the workbook."""

    try:
        xml = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(xml)
    strings: List[str] = []
    for si in root.findall("m:si", ns):
        # A shared string item may be split into multiple ``t`` nodes.
        text = "".join(t.text or "" for t in si.findall(".//m:t", ns))
        strings.append(text)
    return strings


def _load_worksheet(z: ZipFile, shared: List[str]) -> pd.DataFrame:
    """Parse the first worksheet of the workbook into a DataFrame."""

    xml = z.read("xl/worksheets/sheet1.xml")
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(xml)
    sheet_data = root.find("m:sheetData", ns)
    assert sheet_data is not None

    header: List[str] | None = None
    rows: List[List[str]] = []

    for row in sheet_data.findall("m:row", ns):
        r_index = int(row.attrib.get("r", "0"))
        cells: Dict[str, str] = {}
        for c in row.findall("m:c", ns):
            ref = c.attrib["r"]
            col = _column_letter(ref)
            value = ""
            v = c.find("m:v", ns)
            if v is not None and v.text is not None:
                if c.attrib.get("t") == "s":
                    value = shared[int(v.text)]
                else:
                    value = v.text
            cells[col] = value

        if r_index == 8:
            # Header row: expect five columns (A-E)
            header = [cells.get(col, "") for col in ["A", "B", "C", "D", "E"]]
        elif r_index > 8 and header is not None:
            rows.append([cells.get(col, "") for col in ["A", "B", "C", "D", "E"]])

    if header is None:
        raise ValueError("Could not locate header row in worksheet")

    return pd.DataFrame(rows, columns=header)


def read_eredes_xlsx(path: Path) -> pd.DataFrame:
    """Read the E-REDES ``.xlsx`` export into a DataFrame."""

    with ZipFile(path) as zf:
        shared = _parse_shared_strings(zf)
        df = _load_worksheet(zf, shared)
    return df


# ---------------------------------------------------------------------------
# Conversion logic
# ---------------------------------------------------------------------------


def convert(input_file: Path) -> None:
    """Convert the given E-REDES file to the expected CSV output."""

    from datetime import datetime
    from zoneinfo import ZoneInfo

    df = read_eredes_xlsx(input_file)

    # Only keep rows marked as real measurements
    if "Estado" in df.columns:
        df = df[df["Estado"].str.lower() == "real"].copy()

    tz = ZoneInfo("Europe/Lisbon")
    timestamps: List[int] = []
    for date_str, time_str in zip(df["Data"], df["Hora"]):
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M")
        dt = dt.replace(tzinfo=tz)
        timestamps.append(int(dt.timestamp()))

    values = df["Consumo registado, Ativa (kW)"].astype(float).tolist()

    out_df = pd.DataFrame({"timestamp": timestamps, "value": values})

    # Write the resulting CSV to the current working directory instead of the
    # directory containing the source file.  This mirrors the behaviour of the
    # other datasource conversion scripts and ensures that test helpers can
    # easily locate the generated output.
    output_path = Path("elec_feed_in_tariff_1_high_resolution.csv")
    out_df.to_csv(
        output_path,
        index=False,
        header=False,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare E-REDES export for Home Assistant"
    )
    parser.add_argument("-y", "--yes", action="store_true", help="No prompt")
    parser.add_argument("input_file", type=Path, help="Path to .xlsx export")
    args = parser.parse_args(argv)

    if args.yes or input("Are you sure you want to continue [Y/N]?: ").strip().lower().startswith("y"):
        convert(args.input_file)
        return 0
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())

