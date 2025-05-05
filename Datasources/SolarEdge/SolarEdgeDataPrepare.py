import sys
from pathlib import Path

# 1) Add engine to path (simple way to add the engine to the path)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine (supress linter warnings)
import DataPrepareEngine as engine # noqa: E402
from DataPrepareEngine import OutputFileDefinition # noqa: E402

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "SolarEdge"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".json"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "date"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
# Inputfile(s): Json path of the records (only needed for json files)
# Example: inputFileJsonPath: List[str] = ['energy', 'values']
engine.inputFileJsonPath = ["energy", "values"]

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "value",
        [],
        True,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    engine.main()
