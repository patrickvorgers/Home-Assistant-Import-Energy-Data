# Import historical energy through Home Assistant Recorder

This prototype replaces direct SQL writes for one specific scenario:
**prepend older history to an existing, correct Home Assistant statistics series**.

It runs outside Home Assistant and does not require a custom integration. It uses
Recorder's WebSocket commands instead of changing database files. The API schema
was checked against **Core 2026.10.1**. No live import has been performed.

## Files

- `import_energy.py`: input conversion, planning, execution and readback verification.
- `config.example.json`: mappings from generic CSV filenames to destination sensors.
- `requirements.txt`: WebSocket client dependency.
- `test_import_energy.py`: offline behavior tests using a simulated HA API.

## Input format

Use the repository's generic CSV format, without a header:

```text
1704067200,100000
1704070800,105000
1704074400,110000
```

Column 1 is UNIX time in seconds. Column 2 is the cumulative meter reading
**at the start of the interval**, expressed in the configured source unit.
For example, the readings above represent 5 kWh consumption in each of two hours
when the source unit is Wh. The initial 100 kWh meter baseline is not counted
as imported consumption.

The last row closes the previous interval. The importer does not invent another
interval after it. Input must extend through the end of at least the second
complete overlapping HA hour.

Filenames must be `<import_name>_high_resolution.csv` and/or
`<import_name>_low_resolution.csv`. All files in a mapping use the same source
unit. HIGH takes precedence: LOW is included only before the earliest HIGH
timestamp, matching the repository's existing selection rule.

## Supported scope

- Existing Recorder sensor statistics with `has_sum=true`, `mean_type=0`, and
  a recent five-minute sum chain: energy, gas and water counters.
- Wh/kWh/MWh and L/m³ conversion. The **stored statistics unit** is used for
  calculations and API reads, rather than the sensor's display unit.
- Timestamps on exact UTC hour boundaries.
- Multiple sensors, processed separately and tracked separately in the journal.

Empty destinations, external statistics IDs, raw state-history imports,
overwriting overlapping HA measurements and quarter-hour inputs without prior
hour conversion are not supported yet. The prototype does not seed a missing
short-term statistics chain.

## Cumulative-sum alignment

The importer calculates consumption from successive source meter readings and
builds a cumulative source `sum`, starting with the first available interval.
It reads existing hourly and recent five-minute statistics, finds the actual
first HA hour, and imports only source hours before that point.

The required correction is:

```text
adjustment = calculated source sum at the first HA hour - existing HA sum at that hour
```

That same correction is checked against every shared source/HA hour before the
recent compile boundary. Differences must remain within `overlap_tolerance`.
This is an absolute tolerance in the destination statistics unit; the default
is 0.02. Set it according to source resolution and rounding, not merely to
silence a mismatch.

| Hour | Source start reading, kWh | Calculated hour-end sum | Existing HA sum |
|---|---:|---:|---:|
| 00:00 | 100 | 5 | missing |
| 01:00 | 105 | 10 | missing |
| 02:00 | 110 | 12 | 2 |
| 03:00 | 112 | 15 | 5 |
| 04:00 | 115 | closing boundary | — |

The first two hours are imported with sums 5 and 10. Both overlapping hours
require +10, so the existing sums become 12 and 15. Existing HA meter readings
and consumption differences remain unchanged.

An existing high baseline can require a negative correction. The importer
therefore does not blindly add the last imported total to the destination.

## Daily data, gaps and counter resets

The default `gap_policy` is **reject**. Intervals longer than one hour stop
planning because there is no measured hourly distribution.

Explicit `"gap_policy": "uniform"` distributes consumption equally across
the hours in the interval. Daily readings then produce **estimated** hourly
values, not measured hourly values. The plan records the estimated-hour count.
Intervals longer than 31 days are always rejected.

The default `reset_policy` is **reject**. A decreasing reading stops planning.
Explicit `"reset_policy": "zero"` assumes a reset to zero and counts the new
reading as consumption since that reset. Consumption before a reset inside
the interval cannot be recovered from two boundary readings. This is an
explicit assumption, not an exact recovery. Multi-hour reset intervals are
always rejected.

Invalid numbers, NaN, infinity, conflicting duplicate timestamps, empty values,
headers and negative counter readings are rejected. They are never silently
replaced with zero.

## Windows usage

Run the following commands from this directory:

```powershell
python -m pip install -r requirements.txt
```

Copy `config.example.json` to `config.json` and set the actual statistics IDs,
source units and input paths. Relative CSV paths are resolved relative to the
configuration file.

Set a connection URL and an administrator token for the current shell session.
The token is not stored in the plan or journal. The following PowerShell 7
example masks input:

```powershell
$env:HA_URL = 'http://homeassistant.local:8123'
$energyImportToken = Read-Host 'HA administrator token' -MaskInput
$env:HA_TOKEN = $energyImportToken
```

On older PowerShell versions, use an existing secure method to populate the
environment variable. Do not put a token in the configuration or a shared command.

Create a preview first:

```powershell
python import_energy.py plan --config config.json --output import-plan.json
```

This reads HA and writes a local JSON plan. It **does not write to HA**.
Existing plan files are not overwritten.

Review each destination, stored unit, join timestamp, overlap differences,
adjustment, assumptions and historical values. The plan also includes original
sum/state snapshots for verification. It is not a complete database backup.

After reviewing the plan and making a database backup:

```powershell
python import_energy.py apply --plan import-plan.json --backup-confirmed
```

Historical hours are imported in batches of 500 and their sums/states are read
back after each batch. One sum adjustment is then requested from the first
existing HA hour. Final verification checks the imported hours, the original
hourly series plus adjustment, and the original recent five-minute series plus
adjustment.

Planning excludes recent rows at and after a boundary two hours before the
current UTC hour. The adjustment itself shifts all existing sums from the join,
including newer rows. Future Recorder cycles and restart persistence still
require live acceptance testing.

## Interrupted runs and repeated execution

`import-plan.json.journal.json` tracks each sensor through `importing`,
`adjusting` and `complete`.

- During `importing`, resume the **same plan and journal**. Previously imported
  prefix rows must match the plan; rewriting them is deterministic. Existing HA
  rows must still match the original snapshot.
- Before sending the additive correction, `adjusting` is durably recorded.
  On resume, the importer first checks the database. If the expected correction
  is visible, it marks completion without adding the correction again.
- An unconfirmed or partially visible correction stops execution. No automatic
  replay occurs. Inspect Recorder, the plan and journal before deciding how to
  recover.
- At `complete`, repeated execution only verifies and performs no writes.

Keep the plan and journal together. A newly generated plan is not a substitute
for resuming a partial import. Further writing is refused when an unadjusted
plan is older than 24 hours, because snapshots may have changed or been purged.

A lock file prevents concurrent executions of the same plan. A crashed process
can leave the lock behind: inspect processes and the journal before removing
it. This lock does not coordinate other plans, computers or tools. Do not run
other historical-data writers concurrently.

The two API commands do **not** form a combined transaction. Charts may briefly
show an unaligned series between import and adjustment. There is no automatic
rollback. Reversing a confirmed adjustment does not remove imported rows or
constitute a complete restore; full recovery requires a suitable database backup.

## Previewing data already imported previously

Source files may already be represented in HA. Compare their first timestamp
with the actual first destination timestamp before proposing any adjustment.
If no source rows are older, this prepend workflow has no work to do.

A source file starting years after the destination can have a different
relative sum baseline while every overlapping measurement is correct.
That difference is **not** a reason to shift the live destination.

For testing the prepend calculation in this situation, use a separate local
simulation: keep a source window, choose a later hypothetical destination
start, and rebase the simulated destination's sum to its own start. Label that
result as simulated and do not apply its adjustment to the live sensor.

## Validation

```powershell
python -m unittest -v test_import_energy
```

There are 21 offline behavior tests, covering unit conversion, HIGH/LOW
precedence, sum calculation, overlap mismatch, resets, coarse intervals,
existing measurements, both statistics tables, partial imports, lost adjustment
responses, repeated execution, metadata changes, journal handling and the
complete preview/apply workflow. A realistic 24-hour prefix and 48-hour overlap
case checks the join explicitly.

The tests use a simulated HA API. An additional read-only check of personal
Toon CSVs against captured live HA statistics verified selected daily and
hourly measurements and a separately labelled local prepend simulation.
This does not establish live write-path acceptance or compatibility with
every Recorder database.

## References

- [Recorder WebSocket commands, Core 2026.10.1](https://github.com/home-assistant/core/blob/2026.10.1/homeassistant/components/recorder/websocket_api.py)
- [Statistics processing and sum adjustment, Core 2026.10.1](https://github.com/home-assistant/core/blob/2026.10.1/homeassistant/components/recorder/statistics.py)
- [Generic input format, repository v2.9](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/tree/v2.9)
