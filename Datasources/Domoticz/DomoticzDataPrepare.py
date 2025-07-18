import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine  # noqa: E402
from DataPrepareEngine import DataFilter, OutputFileDefinition  # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Domoticz"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".db"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Date"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# When processing SQLite .db files, specify the table name to load
engine.inputFileDbTableName = "meter"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "Value",
        [DataFilter("DeviceRowID", "^2$", True)],
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
