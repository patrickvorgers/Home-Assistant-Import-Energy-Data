import sys
from pathlib import Path
from typing import List

import pandas as pd

# 1) Add engine to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# 2) Import engine
import DataPrepareEngine as engine
from DataPrepareEngine import DataFilter, OutputFileDefinition

# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "Solarman"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".xlsx"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Updated Time"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y/%m/%d"
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = "."
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 0
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0
# Inputfile(s): Name or index of the excel sheet (only needed for excel files containing more sheets,
#               leave at 0 for the first sheet)
engine.inputFileExcelSheetName = 0

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "Production-Today(kWh)",
        [],
        True,
    ),
    OutputFileDefinition(
        "elec_battery_feed_in_high_resolution.csv",
        "Energy Charged-This Day(kWh)",
        [],
        True,
    ),
    OutputFileDefinition(
        "elec_battery_feed_out_high_resolution.csv",
        "Energy Discharged-This Day(kWh)",
        [],
        True,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    engine.main()
