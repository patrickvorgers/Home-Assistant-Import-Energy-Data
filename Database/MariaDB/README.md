<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data">
    <img src="https://raw.githubusercontent.com/patrickvorgers/Home-Assistant-Import-Energy-Data/main/Images/Logo.png" alt="Logo" width="80" height="80">
  </a>

<h1 align="center">How-to MariaDB</h1>

  <p align="center">
How-to for importing historical energy/water data from external datasources into the Home Assistant MariaDB database so that it can be used in the Energy Dashboard.
    <br />
    <br />
  </p>
</div>

<!-- GETTING STARTED -->
<a name="getting-started"></a>
## Getting Started

### Disclaimer

Importing historical energy data into Home Assistant is not simple and requires some technical knowledge. It alters the database of Home Assistant so be sure that you <u><b>always</b></u> have a recent backup of your Home Assistant data!

<a name="How-to"></a>
### How-to

#### Source data preparation
- See the [generic how-to](../../README.md) on how to prepare the source data.

#### Tooling
- Download and install: HeidiSQL https://www.heidisql.com/
- MySQL python library `pip install mysql-connector-python`

#### Home Assistant preparation
- Create a backup of the Home Assistant database
  - Disable recorder while making the backup -> `Developer tools/Actions/Action: Recorder:disable`
- Stop the Home Assistant core
  - `Developer tools/Actions/Action: Home Assistant Core Integration: Stop`

#### Import the data into a temporary table
- Start `HeidiSQL`
- On first run configure the database connection
  - Network type: MariaDB or MySQL (TCP/IP)
  - Hostname/IP: hostname/ip-number of your MariaDB machine
    - In case MariaDB runs on the same machine as Home Assistant this is the same hostname/ip-number of your Home Assistant instance
  - User/password: database user and password
    - The database user and password can be found in the connection string in the `configuration.yaml`
      `
      recorder:
          db_url: mysql://<user>:<password>@core-mariadb/homeassistant?charset=utf8mb4
      `
    - Port: 3306 (default - In case the Home Assistant add-on is used, verify that the port is exposed to the host)
- <b>EXTRA SAFETY STEP</b>: Create a copy of your existing Home Assistant database so that it is possible to quickly move back to the original database.
  - Right click in the left most window and select `Create new -> database`
    - Name: `homeassistant backup`
    - Collation: `utf8mb4_unicode_ci`
  - Right click the `homeassistant` database and select `Export database as SQL`
  - Press `Export` to copy the `homeassistant` database to the `homeassistant backup` database
    - Settings:
      - Database(s): not selected `Drop`, selected `Create`
      - Table(s): not selected `Drop`, selected `Create`
      - Data: `Insert`
      - Output: `Database`
      - Database: `homeassistant backup`
  - In case something goes wrong you can remove the `homeassistant` database and rename the `homeassistant backup` database to the `homeassistant` database.
    - Right click the `homeassistant` database and select `Drop`
    - Right click the `homeassistant backup` database and select `Edit` and change the name into `homeassistant` and press `Ok`
- Run the `ImportData.py` script from the Datasources directory to import the generated CSV files and use the following command-line parameters:
    - `--db-type mariadb`
    - `--host HOST` Host as defined in the HeidiSQL database connection
    - `--user USER` Username as defined in the HeidiSQL database connection
    - `--password PASSWORD` Password as defined in the HeidiSQL database connection
    - `--database homeassistant`
    - `--csv-file CSV_FILE [CSV_FILE ...]` Location of the CSV files generated in the source data preparation step, wildcards are allowed
    - `--verbose`<br><br>
    Example:<br>
`python ImportData.py --db-type mariadb --host localhost --user root --database homeassistant --csv-file "data\*.csv" --verbose`

#### Load import script
- Load SQL file `Import Energy data into Home Assistant.sql` from the MariaDB directory (File -> Load SQL file - Yes on auto-detect file encoding)
- Validate the schema version of the database (Select table: schema_changes and select the data tab on the right and scroll down to the bottom)
  - The script has been tested with schema version 50. With higher versions you should validate if the structure of the `statistics` and `statistics_short_term` tables have changed.
    - Used fields in table `statistics`: `metadata_id`, `state`, `sum`, `start_ts`, `created_ts`
    - Used fields in table `statistics_short_term`: `sum`

#### Determine the sensor configuration
##### Option 1: Use the `Sensors.py` script (GUI)
- Run the `Sensors.py` script from the Database directory to determine the sensor configuration and use the following command-line parameters:
    - `--db-type mariadb`
    - `--host HOST` Host as defined in the HeidiSQL database connection
    - `--user USER` Username as defined in the HeidiSQL database connection
    - `--password PASSWORD` Password as defined in the HeidiSQL database connection
    - `--database homeassistant`<br><br>
    Example:<br>
`python Sensors.py --db-type mariadb --host localhost --user root --database homeassistant`
- Select the target sensors from Home Assistant and the corresponding source import name identifiers.
- Determine the unit of measurement of the source data (`Source unit`). The script will automatically determine the correct correction factor based on the unit of measurement of the source data.
- Determine the `cutoff_new_meter` and `cutoff_invalid_value`. The script will automatically fill in the default values based on the unit of measurement of the target sensor. The different cutoffs are described in the script.
- Press `Generate SQL` which will generate the SQL statements that need to be replaced in the `Import Energy data into Home Assistant.sql` SQL file.
##### Option 2: Manually lookup the sensor information
- Lookup in the `statistics_meta` table the IDs of the sensors (Select table: `statistics_meta` and select the data tab on the right. You can use `filter` to find the ID of the sensor, For instance: `statistic_id LIKE '%sensor.gas_meter%'`)
  - The names of the sensors can be looked up in the Home Assistant Energy dashboard (Settings -> Dashboards -> Energy).
<br>Example:
    ```
        id  statistic_id                                source      unit_of_measurement
        6   sensor.gas_meter                            recorder    m³
        7   sensor.electricity_meter_feed_in_tariff_1   recorder    kWh
        8   sensor.electricity_meter_feed_in_tariff_2   recorder    kWh
        9   sensor.electricity_meter_feed_out_tariff_1  recorder    kWh
        10  sensor.electricity_meter_feed_out_tariff_2  recorder    kWh
        352 sensor.solar_energy_produced_today          recorder    kWh
        450 sensor.battery_energy_feed_in               recorder    kWh
        451 sensor.battery_energy_feed_out              recorder    kWh
        653 sensor.watermeter_quantity_m3               recorder    m³
    ```
- Change the script and remove/comment out the lines of the sensors that are not needed. They can be found at the top of the script by looking up the lines where `/* Change */` has been added in the SQL statement.
- Change the script and update the IDs according to the found IDs in the `statistics_meta` table.
  They can be found at the top of the script by looking up the lines where `/* Change */` has been added in the SQL statement.
  - Determine the `correction` value based on the `unit_of_measurement` of the sensor and the used datasource. The unit of measurement of the datasource can be found in the readme of the datasource.
    The different corrections are described in the script.
  - Determine the `cutoff_new_meter` and `cutoff_invalid_value` values based on the unit of measurement of the target sensor. The different cutoffs are described in the script.

#### Execute import script
- Execute the SQL and wait for it to complete. (Please be patient because this can take some time!)
  - For the first run the `COMMIT` statement at the end of the script can be commented out so that the changes are not written to the database.
    This makes it possible to test the script and see whether it completes without errors.
  - In case of an error correct the error and execute the script again. The script will automatically rollback any changes before trying again.

#### Restart Home Assistant
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the `reboot` command)
- Validate the imported data in the `Energy Dashboard`
  - After validation, the `homeassistant backup` database can be removed. Right-click on `homeassistant backup` and select `Drop` (HeidiSQL).
    Optionally, run the `Cleanup backup data.sql` SQL script to remove the backup data from the `homeassistant` database.
    The backup data can also be removed by using the `ImportData.py` script with the `--cleanup-backup` option.
  - In case of issues, the changes can be rolled back with the `Restore backup data.sql` SQL script.
    This script will revert the changes made by the `Import Energy data into Home Assistant` SQL script.
    Make sure not to wait too long before performing this step, as the Home Assistant recorder will start updating the database with new data, making the backup outdated.
- Enjoy :-)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
