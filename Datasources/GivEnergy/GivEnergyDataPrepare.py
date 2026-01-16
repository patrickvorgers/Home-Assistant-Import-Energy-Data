import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import (  # noqa: E402
    DataFilter,
    IntervalMode,
    OutputFileDefinition,
)

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "GivEnergy"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".json"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "time"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%dT%H:%M:%SZ"
# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = True
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = False
# Inputfile(s): Json path of the records (only needed for json files)
# Example: inputFileJsonPath: List[str] = ['energy', 'values']
engine.inputFileJsonPath = ["data"]

# Name used for the temporary date/time field.
# This needs normally no change only when it conflicts with existing columns.
engine.dateTimeColumnName = "_DateTime"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "total.grid.import",
        [
            DataFilter("status", "^NORMAL$", True),
            DataFilter("is_metered", "^True$", True),
        ],
        IntervalMode.READING_START_INTERVAL,
    ),
    OutputFileDefinition(
        "elec_feed_out_tariff_1_high_resolution.csv",
        "total.grid.export",
        [
            DataFilter("status", "^NORMAL$", True),
            DataFilter("is_metered", "^True$", True),
        ],
        IntervalMode.READING_START_INTERVAL,
    ),
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "total.solar",
        [
            DataFilter("status", "^NORMAL$", True),
            DataFilter("is_metered", "^True$", True),
        ],
        IntervalMode.READING_START_INTERVAL,
    ),
    OutputFileDefinition(
        "elec_battery_feed_out_high_resolution.csv",
        "today.battery.charge",
        [
            DataFilter("status", "^NORMAL$", True),
            DataFilter("is_metered", "^True$", True),
        ],
        IntervalMode.READING_START_INTERVAL,
    ),
    OutputFileDefinition(
        "elec_battery_feed_in_high_resolution.csv",
        "today.battery.discharge",
        [
            DataFilter("status", "^NORMAL$", True),
            DataFilter("is_metered", "^True$", True),
        ],
        IntervalMode.READING_START_INTERVAL,
    ),
]

# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
