# Energy provider: Home Assistant

Home Assistant stores information about all the tracked energy/water sensors within Home Assistant.
Sometimes it is needed to copy the history of an old energy/water sensor to a new energy/water sensor.
In that case it is possible to export the history of the old energy/water sensor and import it into the new energy/water sensor using the import script.
This howto describes how to export data from an existing Home Assistant energy/water sensor into the format that the script can use.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval)
- Electricity consumption - Tariff 2 - High resolution (hour interval)
- Electricity production - Tariff 1 - High resolution (hour interval)
- Electricity production - Tariff 2 - High resolution (hour interval)
- Solar production - High resolution (hour interval)
- Gas consumption - High resolution (hour interval)
- Water consumption - High resolution (hour interval)

**How-to (SQLite):**

##### Tooling
- Download and install: DB Browser (64 bit) for SQLite https://sqlitebrowser.org/ (tested windows version 3.12.2)

##### Export the data
- Start ```DB Browser for SQLite```.
- Open the database (```Open Database```) that has been backed up in the [SQLite how-to](../../SQLite/README.md).
- Lookup in the ```statistics_meta``` table the ID of the sensor for which the data should be exported (Browse Data -> Table: ```statistics_meta```; You can use "filter" to find the ID of the sensor).
<br>Example:
```
        id  statistic_id                                source      unit_of_measurement
        6   sensor.gas_meter                            recorder    m�
        7   sensor.electricity_meter_feed_in_tariff_1   recorder    kWh
        8   sensor.electricity_meter_feed_in_tariff_2   recorder    kWh
        9   sensor.electricity_meter_feed_out_tariff_1  recorder    kWh
        10  sensor.electricity_meter_feed_out_tariff_2  recorder    kWh
        352 sensor.solar_energy_produced_today          recorder    kWh
        653 sensor.watermeter_quantity_m3               recorder    m�
```
- Go to the ```Execute SQL``` tab and paste in the contents of the ```HomeAssistant Export.sql``` file.
- Change the SQL script and fill in the ID of the sensor. The remark ```/* Change */``` has been added in the SQL statement for the line that needs to be changed.
- Execute the SQL and wait for it to complete.
- In the ```Execute SQL``` tab select the 4th button from the right (hovertext: ```Save the results view```). In the dropdown box select ```Export to CSV```.
- Deselect ```Column names in first line``` and use ```,``` as value for ```Field separator``` and press ```Save```.
- Provide the correct name for the file (see [Generic how-to](../../README.md) ```Source data preparation``` section) and save the file.
    - elec_feed_in_tariff_1_high_resolution.csv
    - elec_feed_in_tariff_2_high_resolution.csv
    - elec_feed_out_tariff_1_high_resolution.csv
    - elec_feed_out_tariff_2_high_resolution.csv
    - elec_solar_high_resolution.csv
    - gas_high_resolution.csv
    - water_high_resolution.csv

<br>

**How-to (MariaDB):**

##### Tooling
- Download and install: HeidiSQL https://www.heidisql.com/

##### Export the data
- Start ```HeidiSQL```.
- Open a session to the Home Assistant MariaDB database, see [MariaDB how-to](../../MariaDB/README.md) for information regarding setting up the intial connection and creating a backup of the database.
- Lookup in the ```statistics_meta``` table the ID of the sensor for which the data should be exported (Select table: ```statistics_meta``` and select the data tab on the right. You can use ```filter``` to find the id of the sensor, For instance: ```statistic_id LIKE '%sensor.gas_meter%'```).
<br>Example:
```
        id  statistic_id                                source      unit_of_measurement
        6   sensor.gas_meter                            recorder    m�
        7   sensor.electricity_meter_feed_in_tariff_1   recorder    kWh
        8   sensor.electricity_meter_feed_in_tariff_2   recorder    kWh
        9   sensor.electricity_meter_feed_out_tariff_1  recorder    kWh
        10  sensor.electricity_meter_feed_out_tariff_2  recorder    kWh
        352 sensor.solar_energy_produced_today          recorder    kWh
        653 sensor.watermeter_quantity_m3               recorder    m�
```
- Go to the ```Query*``` tab and paste in the contents of the ```HomeAssistant Export.sql``` file.
- Change the SQL script and fill in the ID of the sensor. The remark ```/* Change */``` has been added in the SQL statement for the line that needs to be changed.
- Execute the SQL and wait for it to complete (Shortcut: F9).
- Right click in the results tab and select ```Export grid rows```.
- Apply the following settings:
    - Encoding: ```UTF-8```
    - Output format: ```Delimited text```
    - Row selection: ```Complete```
    - Include column names: ```deselect```
    - Field separator: ```,```
- Provide the correct name for the file (see [Generic how-to](../../README.md) ```Source data preparation``` section) and save the file (press ```OK```)
    - elec_feed_in_tariff_1_high_resolution.csv
    - elec_feed_in_tariff_2_high_resolution.csv
    - elec_feed_out_tariff_1_high_resolution.csv
    - elec_feed_out_tariff_2_high_resolution.csv
    - elec_solar_high_resolution.csv
    - gas_high_resolution.csv
    - water_high_resolution.csv