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
- See the [generic how-to](../README.md) on how to prepare the source data.

#### Tooling
- Download and install: HeidiSQL https://www.heidisql.com/

#### Home Assistant preparation
- Create a backup of the Home Assistant database
  - Disable recorder while making the backup -> ```Developer tools/Actions/Action: Recorder:disable```
- Stop the Home Assistant core
  - ```Developer tools/Actions/Action: Home Assistant Core Integration: Stop```

#### Import the data
- Start ```HeidiSQL```
- On first run configure the database connection
  - Network type: MariaDB or MySQL (TCP/IP)
  - Hostname/IP: hostname/ip-number of your MariaDB machine
    - In case MariaDB runs on the same machine as Home Assistant this is the same hostname/ip-number of your Home Assistant instance
  - User/password: database user and password
    - The database user and password can be found in the connection string in the ```configuration.yaml```
      ```
      recorder:
          db_url: mysql://<user>:<password>@core-mariadb/homeassistant?charset=utf8mb4
      ```
    - Port: 3306 (default)
- <b>EXTRA SAFETY STEP</b>: Create a copy of your existing Home Assistant database so that it is possible to quickly move back to the original database.
  - Right click in the left most window and select ```Create new -> database```
    - Name: ```homeassistant backup```
    - Collation: ```utf8mb4_unicode_ci```
  - Right click the ```homeassistant``` database and select ```Export database as SQL```
  - Press ```Export``` to copy the ```homeassistant``` database to the ```homeassistant backup``` database
    - Settings:
      - Database(s): not selected ```Drop```, selected ```Create```
      - Table(s): not selected ```Drop```, selected ```Create```
      - Data: ```Insert```
      - Output: ```Database```
      - Database: ```homeassistant backup```
  - In case something goes wrong you can remove the ```homeassistant``` database and rename the ```homeassistant backup``` database to the ```homeassistant``` database.
    - Right click the ```homeassistant``` database and select ```Drop```
    - Right click the ```homeassistant backup``` database and select ```Edit``` and change the name into ```homeassistant``` and press ```Ok```
- Load SQL file ```Import Energy data into Home Assistant.sql``` from the MariaDB directory (File -> Load SQL file - Yes on auto-detect file encoding)
- Validate the schema version of the database (Select table: schema_changes and select the data tab on the right and scroll down to the bottom)
  - The script has been tested with schema version 43. With higher versions you should validate if the structure of the ```statistics``` and ```short_term_statistics``` tables have changed.
    - Used fields in table ```statistics```: ```metadata_id```, ```state```, ```sum```, ```start_ts```, ```created_ts```
    - Used fields in table ```short_term_statistics```: ```sum```
- Import, one at a time, all the created CSV data ```elec*```, ```gas*``` and ```water*``` files (Tools -> Import CSV file...)
  - Settings:
    - Filename: select the CSV file to be imported
    - Ignore first: ```0```
    - REPLACE (duplicates)
    - Fields terminated by: ```,```
    - Lines terminated by: ```\n```
    - Table: scroll down and select ```<new table>```
    - Use the below column definitions and press ```Ok, create table```. Only the column definition has to be changed the name of the table is already filled in.
      ```
      CREATE TABLE `homeassistant test`.<table name> (
        `field1` DOUBLE PRIMARY KEY NOT NULL,
        `field2` DOUBLE NOT NULL
      )
      ```
    - Press ```Import``` and after successfull completion the logwindow will show how many rows were imported.
  - It is possible to load data from multiple CSV's with the same name. The data of the second import is than added to the existing tables. This can be used in case there are multiple energy source providers for different timeperiods. In this case you first import the files from the first energy provider and than then second etc.
    The ```<new table>``` step can be skipped in this case because the table already exists. Instead of selecting ```<new table>``` select the right table in which the data should be imported.
- Lookup in the ```statistics_meta``` table the IDs of the sensors (Select table: ```statistics_meta``` and select the data tab on the right. You can use ```filter``` to find the ID of the sensor, For instance: ```statistic_id LIKE '%sensor.gas_meter%'```)
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
- Change the script and remove/comment out the lines of the sensors that are not needed. They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement.
- Change the script and update the IDs according to the found IDs in the ```statistics_meta``` table.
  They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement.
  - Determine the ```correction``` value based on the ```unit_of_measurement``` of the sensor and the used datasource. The unit of measurement of the datasource can be found in the readme of the datasource.
    The different corrections are described in the script.
  - Determine the ```cutoff_new_meter``` and ```cutoff_invalid_value``` values based on the unit of measurement of the target sensor. The different cutoffs are described in the script.
- Execute the SQL and wait for it to complete. (Please be patient because this can take some time!)
  - For the first run the ```COMMIT``` statement at the end of the script can be commented out so that the changes are not written to the database.
    This makes it possible to test the script and see whether it completes without errors.
  - In case of an error correct the error and execute the script again. The script will automatically rollback any changes before trying again.

#### Restart Home Assistant
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the ```reboot``` command)
- Validate the imported data in the ```Energy Dashboard```
  - After validation the ```homeassistant backup``` database can be removed. Right click on ```homeassistant backup``` and select ```Drop``` (HeidiSQL).
- Enjoy :-)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
