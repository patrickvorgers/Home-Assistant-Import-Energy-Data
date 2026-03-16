# Energy provider: Grafana

Grafana can be used to visualize time series data stored in sources such as InfluxDB.
When energy consumption or production data is available in a Grafana graph, the underlying data can be exported as CSV and used as input for import into Home Assistant.

**Data provided**
- This depends on the data available in the Grafana dashboard and the query behind the graph.

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`
- Tzlocal python library `pip install tzlocal`

**How-to**
- Open Grafana and navigate to the panel containing the energy data to export.
- Set the required time range.
- Ensure that the query is configured to:
    - Aggregate data by **1 hour**
    - Use the **first value** of each hour
    - Apply **fill(previous)** so missing intervals are filled with the last known value
- Open the panel menu, select Inspect - Data, and export the data as a CSV file.
- Download the `GrafanaDataPrepare.py` and `DataPrepareEngine.py` files from the Datasources directory and place them in the same directory as the exported Grafana CSV file.
- Adapt the `GrafanaDataPrepare.py` file to match the structure of the exported CSV:
    - Check whether the timezone parameter is correctly set (if not, set it to the timezone of the data)
    - Data column name (`kWh.first` in the example below)
    - Output file name (`elec_feed_in_tariff_1_high_resolution.csv` in the example below)
```Python
engine.outputFiles = [
    OutputFileDefinition(
        "elec_feed_in_tariff_1_high_resolution.csv",
        "kWh.first",
        [],
        IntervalMode.READING_START_INTERVAL
    ),
]
```
- Execute the python script with as parameter the name of the file that contains the exported data `python GrafanaDataPrepare.py "PV 11 meter-data-2026-03-15 12_41_54.csv"`. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to