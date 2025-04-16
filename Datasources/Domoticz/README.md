# Energy provider: Domoticz

Domoticz is a home automation system that allows you to monitor and control various devices in your home.
It stores data in a SQLite database, which can be accessed using SQL queries.
Data from this database can be extracted and transformed so that it can be imported into Home Assistant.

**Data provided**
- Any metered sensor data stored in the Domoticz SQLite database can be used.

**Tooling needed**
- Python 3
- Pandas python library `pip install pandas`

**Preparation**
- Update and create in the `DomoticzDataPrepare.py` script the output file definitions for the data that needs to be exported from the Domoticz database.
Define an output file definition for each dataset that needs to be exported.
The `DeviceRowID` can be looked up in the Domoticz user interface by looking up the device-id of the sensor.
The device-id must be enclosed in `^` and `$` to match the exact string (regular expression).
```python
# List of one or more output file definitions
outputFiles = [
    OutputFileDefinition(
        "elec_solar_high_resolution.csv",
        "Value",
        [DataFilter("DeviceRowID", "^2$", True)],
        False,
    ),
]
```

**How-to**
- Copy the SQLite database file from Domoticz to the same directory as the DomoticzDataPrepare.py script.
- Download the `DomoticzDataPrepare.py` file and put it in the same directory as the Domoticz database file.
- Execute the python script with as parameter the name of the Domoticz SQLite database file `python DomoticzDataPrepare.py domoticz.db`.
  The python script creates the needed file(s) for the generic import script.
- Follow the steps in the overall how-to
