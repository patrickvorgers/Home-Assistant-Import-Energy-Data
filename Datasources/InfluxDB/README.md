# Energy provider: InfluxDB Chronograf

InfuxDB Chronograf is a time series database that can be used to store and analyze energy consumption and production data.
It provides a powerful query language and visualization tools to help you understand your energy usage patterns.
This data can be exported using the Chronograf interface and and used to import into Home Assistant.

**Data provided**
- Depends on the data you have stored in InfluxDB, but typically includes:

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Open the InfluxDB Chronograf interface and navigate to the data you want to export.
- Select the time range and the fields you want to export, aggregate by 1 hour and use the first value of the hour.
- Export the data as a CSV file
- Download the `InfluxDbChronografDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded InfluxDB Chronograf data
- Adapt the `InfluxDbChronografDataPrepare.py` file to match the structure of your exported data:
    - Data column name (`kWh.first_value` in the example below)
    - Output file name (`elec_feed_in_tariff_1_high_resolution.csv` in the example below)
```Python
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "kWh.first_value",
        [],
        IntervalMode.READING_START_INTERVAL
    ),
]
```
- Execute the python script with as parameter the name of the file that contains the exported data `python InfluxDbChronografDataPrepare.py 2026-03-14-21-49 Chronograf Data.csv`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to