#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests

BASE_URL = "https://api.givenergy.cloud/v1"


def _parse_date(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError("Invalid date. Expected YYYY-MM-DD") from e


def _daterange_inclusive(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    cur = start
    one_day = dt.timedelta(days=1)
    while cur <= end:
        yield cur
        cur += one_day


def _build_headers(api_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _raise_for_status(resp: requests.Response) -> None:
    if resp.status_code == 403:
        raise PermissionError(
            "403 Forbidden. Check API token scopes and whether a Third-Party API Lock is enabled."
        )
    if resp.status_code == 401:
        raise PermissionError("401 Unauthorized. Check your API token.")
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")


def _read_token_from_file(path: str) -> str:
    """Read API token from a text file (whitespace/newlines are stripped).
    Returns "" and prints an error message if the file cannot be read.
    """
    p = Path(path)

    try:
        content = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: API token file not found: {p.resolve()}")
        return ""
    except OSError as e:
        print(f"Error: Could not read API token file: {p.resolve()} ({e})")
        return ""

    token = content.strip()
    if not token:
        print(f"Error: API token file is empty: {p.resolve()}")
        return ""

    return token


def fetch_day(*, serial: str, api_token: str, datestring: str) -> Dict[str, Any]:
    """Fetch a full day of data and merge all paginated pages into one payload."""

    url = f"{BASE_URL}/inverter/{serial}/data-points/{datestring}"
    headers = _build_headers(api_token)

    page = 1
    all_points: List[Dict[str, Any]] = []
    first_payload: Optional[Dict[str, Any]] = None

    while True:
        resp = requests.get(url, headers=headers, params={"page": page})
        _raise_for_status(resp)

        payload = resp.json()
        if first_payload is None:
            first_payload = payload

        points = payload.get("data") or []
        if not isinstance(points, list):
            raise RuntimeError("Unexpected response: 'data' is not a list")
        all_points.extend(points)

        meta = payload.get("meta") or {}
        last_page = int(meta.get("last_page", 1) or 1)
        if page >= last_page:
            break
        page += 1

    combined_meta = {
        "current_page": 1,
        "from": 1 if all_points else 0,
        "last_page": 1,
        "to": len(all_points),
        "total": len(all_points),
        "per_page": len(all_points),
    }

    combined: Dict[str, Any] = {}
    if isinstance(first_payload, dict):
        combined.update({k: v for k, v in first_payload.items() if k not in ("data", "meta")})

    combined["data"] = all_points
    combined["meta"] = combined_meta
    return combined


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        # Use a standard, human-readable indentation
        json.dump(payload, f, indent=4)



def main() -> int:
    print(f"Grab GivEnergy data\n")
    print(
        f"This python script grabs the GivEnergy daily data which can be used in the conversion script.\n"
    )
    
    parser = argparse.ArgumentParser(
        description=(
            "Download daily JSON data-points from the GivEnergy Cloud API and store them as files. "
            "This script only downloads and writes JSON."
        )
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt.",
    )

    parser.add_argument(
        "--api-token-file",
        type=str,
        required=True,
        help="Path to a file containing the Portal API token (whitespace/newlines are ignored).",
    )

    parser.add_argument(
        "--serial",
        type=str,
        required=True,
        help="Inverter serial number.",
    )

    parser.add_argument(
        "start_date",
        type=_parse_date,
        help="Start date (YYYY-MM-DD).",
    )

    parser.add_argument(
        "end_date",
        nargs="?",
        type=_parse_date,
        default=None,
        help="End date (YYYY-MM-DD), inclusive. Defaults to start_date.",
    )

    args = parser.parse_args()

    api_token = _read_token_from_file(args.api_token_file)
    if not api_token:
        return 2

    serial = args.serial.strip()

    start: dt.date = args.start_date
    end: dt.date = args.end_date if args.end_date is not None else args.start_date

    if end < start:
        print("Error: end_date must be on or after start_date")
        return 2

    print("GivEnergy JSON Downloader")
    print(f"Serial: {serial}")
    print(f"Date range: {start.isoformat()} .. {end.isoformat()} (inclusive)")
    print("Output: current directory")
    print("WARNING: Existing files WILL be overwritten.")
    print("")

    if not args.yes:
        answer = input("Continue? [y/N]: ").strip().lower()
        if not answer.startswith("y"):
            print("Aborted.")
            return 0

    for day in _daterange_inclusive(start, end):
        datestring = day.isoformat()
        target = Path(f"MeterData_{datestring}.json")

        if target.exists():
            print(f"Downloading {datestring} -> {target} (overwriting)")
        else:
            print(f"Downloading {datestring} -> {target}")

        try:
            payload = fetch_day(serial=serial, api_token=api_token, datestring=datestring)
            write_json(target, payload)
            count = len(payload.get("data") or [])
            print(f"  Wrote {count} points")
        except Exception as e:
            print(f"  Failed: {e}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
