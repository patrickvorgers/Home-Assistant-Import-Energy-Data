# Energy provider: InfluxDB Chronograf

InfuxDB Chronograf is a time series database that can be used to store and analyze energy consumption and production data.
It provides a powerful query language and visualization tools to help you understand your energy usage patterns.
This data can be exported using the Chronograf interface and and used to import into Home Assistant.

**Data provided**
- This depends on the data that is stored in InfluxDB.

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Open the InfluxDB Chronograf interface and navigate to the data you want to export.
- Select InfluxQL as the query language and write the query to retrieve the desired data.
<br>
<img width="1778" height="1157" alt="InfluxDB InfluxQL" src="https://github.com/user-attachments/assets/92a62e3e-4eed-4fce-9872-447f8a6092fd" />
<br>
- Set the required time range.
- Ensure that the query is configured to:
    - Aggregate data by **1 hour**
    - Use the **first value** of each hour
    - Apply **fill(previous)** so missing intervals are filled with the last known value
- Export the data as a CSV file
- Download the `InfluxDbChronografDataPrepare.py` and the `DataPrepareEngine.py` (Datasources directory) files and put it in the same directory as the downloaded InfluxDB Chronograf data
- Adapt the `InfluxDbChronografDataPrepare.py` file to match the structure of the exported CSV:
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
- Execute the python script with as parameter the name of the file that contains the exported data `python InfluxDbChronografDataPrepare.py "2026-03-14-21-49 Chronograf Data.csv"`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to
