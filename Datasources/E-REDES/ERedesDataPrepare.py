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
engine.energyProviderName = "E-Redes"

# Inputfile(s): filename extension
engine.inputFileNameExtension = ".xlsx"
# Inputfile(s): Name of the column containing the date of the reading.
#               Use this in case date and time is combined in one field.
#               Use the numerical column index in case the column name is not available.
engine.inputFileDateColumnName = "Data"
# Inputfile(s): Name of the column containing the time of the reading.
#               Leave empty in case date and time is combined in one field.
engine.inputFileTimeColumnName = "Hora"
# Inputfile(s): Date/time format used in the datacolumn.
#               Combine the format of the date and time in case date and time are two seperate fields.
engine.inputFileDateTimeColumnFormat = "%Y/%m/%d %H:%M"
# Inputfile(s): Date/time UTC indication
#               Set to True in case the date/time is in UTC, False in case it is in local time.
engine.inputFileDateTimeIsUTC = False
# Inputfile(s): Name of the timezone of the input data
#               The IANA timezone name of the input data (so that DST can be correctly applied).
#               Example: "Europe/Amsterdam", "America/New_York".
#               Leave as empty string to auto-detect from the local machine.
#               Setting is only needed when the setting inputFileDateTimeIsUTC is False.
engine.inputFileTimeZoneName = "Europe/Lisbon"
# Inputfile(s): Only use hourly data (True) or use the data as is (False)
#               In case of True, the data will be filtered to only include hourly data.
#               It takes into account in case the data needs to be recalculated (source data not increasing).
#               Home Assistant uses hourly data, higher resolution will work but will impact performance.
engine.inputFileDateTimeOnlyUseHourly = True
# Inputfile(s): Invalid values in the input file will be removed otherwise they will be replaced with 0.
engine.inputFileDataRemoveInvalidValues = False
# Inputfile(s): Decimal token being used in the input file (csv and excel files)
engine.inputFileDataDecimal = ","
# Inputfile(s): Number of header rows in the input file (csv and excel files)
engine.inputFileNumHeaderRows = 7
# Inputfile(s): Number of footer rows in the input file (csv and excel files)
engine.inputFileNumFooterRows = 0
# Inputfile(s): Name or index of the excel sheet (only needed for excel files containing more sheets,
#               leave at 0 for the first sheet)
engine.inputFileExcelSheetName = 0

# Name used for the temporary date/time field.
# This needs normally no change only when it conflicts with existing columns.
engine.dateTimeColumnName = "_DateTime"

# List of one or more output file definitions
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "Consumo registado, Ativa (kW)",
        [DataFilter("Estado", "Real", True)],
        IntervalMode.USAGE,
    ),
]


# 4) Invoke DataPrepare engine
if __name__ == "__main__":
    engine.main()
