"""Conservative prepend importer for HA Recorder, API schema checked against Core 2026.10.1.

CSV: UNIX seconds, cumulative meter reading AT START of interval (no header).
The last reading is a boundary, not another interval to import.
Plan is read-only for HA. Apply requires a saved plan and a separate journal.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

HOUR = 3600
FORMAT = 1
UNIT_FAMILIES = (
    {"Wh": 1.0, "kWh": 1000.0, "MWh": 1000000.0},
    {"L": 1.0, "m³": 1000.0},
)


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def epoch(value):
    if isinstance(value, str):
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    # Recorder WebSocket returns start/end as UNIX milliseconds.
    number = float(value) / 1000
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError("Unexpected Recorder timestamp")
    return int(number)


def finite(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("NaN and infinity are not valid measurements")
    return number


def close(a, b, tolerance):
    return a is not None and b is not None and abs(a - b) <= tolerance


def unit_factor(source, target):
    for family in UNIT_FAMILIES:
        if source in family and target in family:
            return family[source] / family[target]
    raise ValueError(f"Unsupported unit conversion: {source!r} -> {target!r}")


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(data):
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def save_json(path, data, exclusive=False):
    path = Path(path)
    if exclusive:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        return
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


class HAClient:
    def __init__(self, url, token):
        if not token:
            raise ValueError("Set HA_TOKEN to a Home Assistant administrator token")
        try:
            import websocket
        except ImportError as exc:
            raise ValueError("Install requirements.txt first") from exc
        parsed = urlsplit(url.rstrip("/"))
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("HA_URL must be a full http(s) URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Do not put credentials, query parameters or fragments in HA_URL")
        self.url = url.rstrip("/")
        endpoint = urlunsplit(("wss" if parsed.scheme == "https" else "ws",
                              parsed.netloc, parsed.path.rstrip("/") + "/api/websocket", "", ""))
        self.ws = websocket.create_connection(endpoint, timeout=90)
        self.sequence = 0
        if self.receive().get("type") != "auth_required":
            self.ws.close()
            raise ValueError("Unexpected authentication handshake")
        self.ws.send(json.dumps({"type": "auth", "access_token": token}))
        reply = self.receive()
        if reply.get("type") != "auth_ok":
            self.ws.close()
            raise ValueError("Home Assistant authentication failed")
        self.version = reply.get("ha_version", "unknown")

    def receive(self):
        return json.loads(self.ws.recv())

    def call(self, command, **arguments):
        self.sequence += 1
        message = {"id": self.sequence, "type": command, **arguments}
        self.ws.send(json.dumps(message, allow_nan=False))
        while True:
            reply = self.receive()
            if reply.get("id") != self.sequence:
                continue
            if reply.get("type") != "result" or not reply.get("success"):
                raise RuntimeError(f"{command}: {reply.get('error', 'unexpected response')}")
            return reply.get("result")

    def metadata(self):
        return {row["statistic_id"]: row for row in
                self.call("recorder/list_statistic_ids", statistic_type="sum")}

    def rows(self, sensor, start, end, period="hour"):
        result = self.call(
            "recorder/statistics_during_period", statistic_ids=[sensor["statistic_id"]],
            start_time=iso(start), end_time=iso(end), period=period,
            units={sensor["unit_class"]: sensor["unit"]}, types=["sum", "state"],
        )
        rows = []
        for row in result.get(sensor["statistic_id"], []):
            ts = epoch(row["start"])
            if start <= ts < end:
                rows.append({"ts": ts, "sum": finite(row["sum"]) if row.get("sum") is not None else None,
                             "state": finite(row["state"]) if row.get("state") is not None else None})
        return sorted(rows, key=lambda row: row["ts"])

    def close(self):
        self.ws.close()


def read_source(config, directory, target_unit):
    """HIGH wins; LOW is used only before the first HIGH timestamp, like the repo."""
    by_resolution = {"HIGH": {}, "LOW": {}}
    fingerprints = []
    factor = unit_factor(config["source_unit"], target_unit)
    for filename in config["files"]:
        path = (directory / filename).resolve()
        suffix = next((kind for kind in by_resolution
                       if path.name == f"{config['import_name']}_{kind.lower()}_resolution.csv"), None)
        if suffix is None:
            raise ValueError(f"Unexpected CSV filename: {path.name}")
        fingerprints.append({"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        with path.open(newline="", encoding="utf-8-sig") as stream:
            for line, row in enumerate(csv.reader(stream), 1):
                if len(row) != 2:
                    raise ValueError(f"{path.name}:{line}: expected exactly two columns")
                try:
                    timestamp = Decimal(row[0].strip())
                    if not timestamp.is_finite() or timestamp != timestamp.to_integral_value():
                        raise ValueError("UNIX timestamp must be a finite integer")
                    ts = int(timestamp)
                    value = finite(row[1]) * factor
                    if not math.isfinite(value) or value < 0:
                        raise ValueError("Expected a finite, nonnegative cumulative reading")
                    if ts < 0 or ts % HOUR:
                        raise ValueError("This prototype requires readings on full UTC hours")
                except (ValueError, InvalidOperation) as exc:
                    raise ValueError(f"{path.name}:{line}: {exc}") from exc
                if ts in by_resolution[suffix] and by_resolution[suffix][ts] != value:
                    raise ValueError(f"Conflicting duplicate timestamp in {path.name}:{line}")
                by_resolution[suffix][ts] = value
    high = by_resolution["HIGH"]
    first_high = min(high) if high else math.inf
    readings = {ts: val for ts, val in by_resolution["LOW"].items() if ts < first_high}
    readings.update(high)
    if len(readings) < 3:
        raise ValueError("Need at least three readings, including the closing boundary")
    return sorted(readings.items()), fingerprints


def source_statistics(readings, gap_policy="reject", reset_policy="reject"):
    """Meter readings at interval start -> hour-end state and cumulative consumption."""
    if gap_policy not in ("reject", "uniform") or reset_policy not in ("reject", "zero"):
        raise ValueError("Unknown gap/reset policy")
    total = 0.0
    output = []
    estimates = resets = 0
    for (start, before), (end, after) in zip(readings, readings[1:]):
        hours = (end - start) // HOUR
        if hours <= 0 or (end - start) % HOUR:
            raise ValueError("Source intervals must be positive whole hours")
        if hours > 24 * 31:
            raise ValueError("An interval exceeds 31 days; inspect the input")
        if hours != 1 and gap_policy == "reject":
            raise ValueError(f"Missing hourly boundaries at {iso(start)}: interval {hours} hours; "
                             "uniform distribution requires explicit gap_policy=uniform")
        delta = after - before
        reset = delta < 0
        if reset:
            if reset_policy == "reject":
                raise ValueError(f"Counter decrease at {iso(end)}; inspect or explicitly choose reset_policy=zero")
            delta = after  # Explicit assumption: reset to zero, no recoverable pre-reset consumption.
            resets += 1
            if hours > 1:
                raise ValueError("Cannot distribute a reset across a multi-hour interval")
        if hours > 1:
            estimates += hours
        for offset in range(hours):
            total += delta / hours
            state = after if reset else before + delta * (offset + 1) / hours
            output.append({"ts": start + offset * HOUR, "state": state, "sum": total})
    return output, {"estimated_hours": estimates, "assumed_zero_resets": resets}


def make_sensor_plan(config, metadata, source, existing, short, end, notes):
    tolerance = finite(config.get("overlap_tolerance", 0.02))
    if tolerance <= 0:
        raise ValueError("overlap_tolerance must be positive, in destination units")
    if not existing or existing[0]["sum"] is None:
        raise ValueError("This prototype requires an existing destination with hourly sum statistics")
    if any(row["sum"] is None for row in existing):
        raise ValueError("Destination contains NULL sums; repair or inspect before importing")
    cutoff = existing[0]["ts"]
    old = {row["ts"]: row for row in existing}
    new = {row["ts"]: row for row in source}
    historical = [row for row in source if row["ts"] < cutoff]
    if not historical:
        raise ValueError("No source hours precede the destination; do not use a new plan to resume")
    if historical[-1]["ts"] + HOUR != cutoff or cutoff not in new or cutoff + HOUR not in new:
        raise ValueError("Need a continuous prefix and at least two complete overlapping hours at the join")
    overlap = [ts for ts in sorted(old) if ts in new]
    if cutoff + HOUR not in overlap:
        raise ValueError("Destination lacks the second overlap hour")
    offsets = [new[ts]["sum"] - old[ts]["sum"] for ts in overlap]
    correction = offsets[0]
    spread = max(abs(offset - correction) for offset in offsets)
    if spread > tolerance:
        raise ValueError(f"Overlap consumption differs by {spread:g} {metadata['statistics_unit_of_measurement']}; "
                         f"allowed {tolerance:g}. No unambiguous constant sum correction")
    if abs(correction) <= 1e-10:
        correction = 0.0
    return {
        "statistic_id": config["statistic_id"], "unit": metadata["statistics_unit_of_measurement"],
        "unit_class": metadata["unit_class"], "metadata": {
            "statistic_id": config["statistic_id"], "source": "recorder", "name": metadata.get("name"),
            "unit_of_measurement": metadata["statistics_unit_of_measurement"], "unit_class": metadata["unit_class"],
            "mean_type": metadata["mean_type"], "has_sum": True,
        },
        "cutoff": cutoff, "end": end, "correction": correction, "tolerance": tolerance,
        "overlap_hours": len(overlap), "overlap_max_difference": spread,
        "historical": historical, "before_hour": existing, "before_5minute": short,
        "source_notes": notes,
    }


def build_plan(client, config_path):
    path = Path(config_path).resolve()
    config = json.loads(path.read_text(encoding="utf-8"))
    metadata = client.metadata()
    now = int(time.time())
    end = (now // HOUR - 2) * HOUR  # Avoid the hourly compile window.
    plans = []
    seen = set()
    for mapping in config["sensors"]:
        sid = mapping["statistic_id"]
        if sid in seen:
            raise ValueError("Each destination must occur once in the config")
        seen.add(sid)
        meta = metadata.get(sid)
        if not meta or meta.get("source") != "recorder" or not sid.startswith("sensor."):
            raise ValueError(f"{sid}: expected existing recorder sensor statistics")
        if not meta.get("has_sum") or meta.get("mean_type") != 0:
            raise ValueError(f"{sid}: expected a sum-only meter (mean_type=0)")
        unit = meta.get("statistics_unit_of_measurement")
        if meta.get("unit_class") not in ("energy", "volume"):
            raise ValueError(f"{sid}: only energy/gas/water counters are supported")
        readings, files = read_source(mapping, path.parent, unit)
        source, notes = source_statistics(readings, mapping.get("gap_policy", "reject"),
                                          mapping.get("reset_policy", "reject"))
        sensor = {"statistic_id": sid, "unit_class": meta["unit_class"], "unit": unit}
        # Query from the epoch to discover the actual oldest destination row, including older history.
        existing = client.rows(sensor, 0, end)
        short = client.rows(sensor, max(0, end - 7 * 86400), end, "5minute")
        plan = make_sensor_plan(mapping, meta, source, existing, short, end, notes)
        if not short or short[-1]["sum"] is None or end - short[-1]["ts"] > HOUR:
            raise ValueError(f"{sid}: no recent short-term sum chain; this prototype cannot seed an empty chain")
        if any(row["sum"] is None for row in short):
            raise ValueError(f"{sid}: short-term NULL sums need inspection")
        plan["files"] = files
        plans.append(plan)
    if not plans:
        raise ValueError("No sensors configured")
    return {"format": FORMAT, "created": now, "ha_version": client.version, "ha_url": client.url,
            "sensors": plans, "plan_id": digest(plans)}


def rows_match(actual, expected, tolerance, with_state=False):
    lookup = {row["ts"]: row for row in actual}
    for row in expected:
        found = lookup.get(row["ts"])
        if not found or not close(found.get("sum"), row["sum"], tolerance):
            return False
        if with_state:
            expected_state = row.get("state")
            actual_state = found.get("state")
            if expected_state is None:
                if actual_state is not None:
                    return False
            elif not close(actual_state, expected_state, tolerance):
                return False
    return True


def expected_shift(rows, correction):
    return [{**row, "sum": row["sum"] + correction} for row in rows]


def wait_for(check, timeout=90):
    deadline = time.monotonic() + timeout
    while True:
        if check():
            return
        if time.monotonic() >= deadline:
            raise RuntimeError("Readback did not confirm the expected result; inspect journal before continuing")
        time.sleep(2)


def apply_sensor(client, sensor, status, persist, batch_size=500):
    sid = sensor["statistic_id"]
    tolerance = sensor["tolerance"]
    delta = sensor["correction"]
    end = sensor["end"]
    cutoff = sensor["cutoff"]
    historical = sensor["historical"]
    before = sensor["before_hour"]
    short = sensor["before_5minute"]

    def final_matches():
        hourly = client.rows(sensor, historical[0]["ts"], end)
        five = client.rows(sensor, short[0]["ts"], end, "5minute")
        return (rows_match(hourly, historical, tolerance, True)
                and rows_match(hourly, expected_shift(before, delta), tolerance, True)
                and rows_match(five, expected_shift(short, delta), tolerance, True))

    phase = status.get("phase", "new")
    if phase not in ("new", "importing", "adjusting", "complete"):
        raise ValueError(f"Unknown journal phase: {phase}")
    if phase in ("adjusting", "complete"):
        # Ambiguous network failures are NEVER retried as another additive correction.
        wait_for(final_matches)
        status["phase"] = "complete"
        persist()
        return
    actual = client.rows(sensor, cutoff, end)
    actual_short = client.rows(sensor, short[0]["ts"], end, "5minute")
    if not rows_match(actual, before, tolerance, True) or not rows_match(actual_short, short, tolerance, True):
        raise RuntimeError(f"{sid}: destination changed since planning; refusing to write")
    existing_prefix = client.rows(sensor, historical[0]["ts"], cutoff)
    source_by_ts = {row["ts"]: row for row in historical}
    if phase == "new" and existing_prefix:
        raise RuntimeError(f"{sid}: history appeared before cutoff after planning")
    if any(row["ts"] not in source_by_ts or not rows_match([row], [source_by_ts[row['ts']]], tolerance, True)
           for row in existing_prefix):
        raise RuntimeError(f"{sid}: conflicting partial import")
    status["phase"] = "importing"
    persist()
    for start in range(0, len(historical), batch_size):
        batch = historical[start:start + batch_size]
        stats = [{"start": iso(row["ts"]), "state": row["state"], "sum": row["sum"]} for row in batch]
        client.call("recorder/import_statistics", metadata=sensor["metadata"], stats=stats)
        wait_for(lambda: rows_match(client.rows(sensor, batch[0]["ts"], batch[-1]["ts"] + HOUR),
                                    batch, tolerance, True))
        status["confirmed_hours"] = start + len(batch)
        persist()
    # Check existing old data once more before the additive correction.
    if not rows_match(client.rows(sensor, cutoff, end), before, tolerance, True):
        raise RuntimeError(f"{sid}: existing sums changed while importing")
    status["phase"] = "adjusting"  # Persist intent BEFORE sending a non-idempotent command.
    persist()
    if delta:
        client.call("recorder/adjust_sum_statistics", statistic_id=sid, start_time=iso(cutoff),
                    adjustment=delta, adjustment_unit_of_measurement=sensor["unit"])
    wait_for(final_matches)
    status["phase"] = "complete"
    persist()


def apply_plan(client, plan_path, batch_size=500):
    path = Path(plan_path).resolve()
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("format") != FORMAT or plan.get("plan_id") != digest(plan["sensors"]):
        raise ValueError("Plan format/hash mismatch; do not edit saved plans")
    if plan["ha_version"] != client.version:
        raise ValueError("Home Assistant version changed since planning")
    if plan.get("ha_url") != client.url:
        raise ValueError("Home Assistant URL differs from the planned destination")
    journal_path = path.with_name(path.name + ".journal.json")
    lock_path = path.with_name(path.name + ".lock")
    # Prevent concurrent copies using the same plan. A crash leaves the lock for inspection.
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Plan is locked: {lock_path.name}. Inspect running processes/journal first") from exc
    os.close(lock_fd)
    try:
        journal = json.loads(journal_path.read_text()) if journal_path.exists() else {
            "plan_id": plan["plan_id"], "sensors": {}}
        if journal.get("plan_id") != plan["plan_id"]:
            raise ValueError("Journal belongs to another plan")
        metadata = client.metadata()
        for sensor in plan["sensors"]:
            sid = sensor["statistic_id"]
            current = metadata.get(sid, {})
            if (current.get("statistics_unit_of_measurement") != sensor["unit"]
                    or current.get("unit_class") != sensor["unit_class"]
                    or current.get("mean_type") != sensor["metadata"]["mean_type"]
                    or current.get("source") != "recorder" or not current.get("has_sum")):
                raise ValueError(f"{sid}: destination metadata changed")
            state = journal["sensors"].setdefault(sid, {})
            if state.get("phase") not in ("adjusting", "complete") and time.time() - plan["created"] > 86400:
                raise ValueError("Plan is older than 24 hours; inspect partial work before proceeding")
            apply_sensor(client, sensor, state, lambda: save_json(journal_path, journal), batch_size)
            print(f"Verified: {sid}")
    finally:
        lock_path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.environ.get("HA_URL"))
    commands = parser.add_subparsers(dest="command", required=True)
    preview = commands.add_parser("plan", help="Read HA and create a local preview; no HA writes")
    preview.add_argument("--config", required=True)
    preview.add_argument("--output", default="import-plan.json")
    execute = commands.add_parser("apply", help="Write a reviewed plan and verify both statistic tables")
    execute.add_argument("--plan", required=True)
    execute.add_argument("--backup-confirmed", action="store_true")
    execute.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args(argv)
    if not args.url:
        parser.error("Set HA_URL or provide --url")
    if args.command == "apply" and not args.backup_confirmed:
        parser.error("apply requires --backup-confirmed after making a database backup")
    if args.command == "apply" and not 1 <= args.batch_size <= 2000:
        parser.error("batch size must be between 1 and 2000")
    client = HAClient(args.url, os.environ.get("HA_TOKEN"))
    try:
        if args.command == "plan":
            plan = build_plan(client, args.config)
            save_json(args.output, plan, exclusive=True)
            for sensor in plan["sensors"]:
                print(f"{sensor['statistic_id']}: {len(sensor['historical'])} older hours, "
                      f"join {iso(sensor['cutoff'])}, sum adjustment {sensor['correction']:+g} {sensor['unit']}, "
                      f"{sensor['overlap_hours']} checked overlap hours; assumptions {sensor['source_notes']}")
            print(f"Preview saved to {args.output}; Home Assistant was not modified")
        else:
            apply_plan(client, args.plan, args.batch_size)
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)
