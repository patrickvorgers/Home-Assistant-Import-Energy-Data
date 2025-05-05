import pandas as pd
import sys
from pathlib import Path
from typing import List


# 1) Add engine to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# 2) Import engine
import DataPrepareEngine as engine
from DataPrepareEngine import DataFilter, OutputFileDefinition


# 3) Override DataPrepare engine globals
# Name of the energy provider
engine.energyProviderName = "P1Mon"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".xlsx"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "TIMESTAMP"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y-%m-%d %H:%M:%S"
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
        "water_high_resolution.csv",
        "VERBR_IN_M3_TOTAAL",
        [],
        False,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == '__main__':
    engine.main()
