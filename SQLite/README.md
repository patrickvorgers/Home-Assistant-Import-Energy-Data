<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data">
    <img src="https://raw.githubusercontent.com/patrickvorgers/Home-Assistant-Import-Energy-Data/main/Images/Logo.png" alt="Logo" width="80" height="80">
  </a>

<h1 align="center">How-to SQLite</h1>

  <p align="center">
How-to for importing historical energy/water data from external datasources into the Home Assistant SQLite database so that it can be used in the Energy Dashboard.
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
- Download and install: DB Browser (64 bit) for SQLite https://sqlitebrowser.org/ (tested windows version 3.12.2)
    - Make sure that the minimum SQLite engine version is 3.35.0. The can be checked via: Help -> About
- Download and install/configure: WinSCP (https://winscp.net/eng/download.php)

#### Home Assistant preparation
- Create a backup of the Home Assistant database
    - Disable recorder while making the backup -> ```Developer tools/Actions/Action: Recorder:disable```
- Download the created backup
- Stop the Home Assistant core
    - ```Developer tools/Actions/Action: Home Assistant Core Integration: Stop```
- Home Assistant data: 
    - extract: ```home-assistant_v2.db``` (from ```backup.tar``` extract ```homeassistant.tar.gz``` from ```data``` folder). As an alternative it is also possible to download the ```home-assistant_v2.db``` directly from the Home Assistant ```config``` directory (For example: use WinSCP in combination with the Home Assistant SSH addon). In case of this method make sure that you didn't skip the step to create a backup so that you can always restore this version of the database!

#### Import the data
- Start ```DB Browser for SQLite```
- Open project ```Import Energy data into Home Assistant.sqbpro```.
    - If the database is not loaded directly you have to open the ```home-assistant_v2.db``` database manually ("Open Database").
- Validate the schema version of the database (Browse Data -> Table: schema_changes)
    - The script has been tested with schema version 43. With higher versions you should validate if the structure of the ```statistics``` and ```short_term_statistics``` tables have changed.
        - Used fields in table ```statistics```: ```metadata_id```, ```state```, ```sum```, ```start_ts```, ```created_ts```
        - Used fields in table ```short_term_statistics```: ```sum```
- Import, one at a time, all the created CSV data ```elec*```, ```gas*``` and ```water*``` files (File -> Import -> Table from CSV file...)
    - It is possible to load data from multiple CSV's with the same name. The data of the second import is than added to the existing tables. This can be used in case there are multiple energy source providers for different timeperiods. In this case you first import the files from the first energy provider and than then second etc.
- Lookup in the ```statistics_meta``` table the ID's of the sensors (Browse Data -> Table: ```statistics_meta```; You can use "filter" to find the id of the sensor)
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
        653 sensor.watermeter_quantity_m3               recorder    m³
```
- Change the script and remove/comment out the lines of the sensors that are not needed. They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement.
- Change the script and update the ID's according to the found ID's in the ```statistics_meta``` table.
  They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement.
    - Determine the ```correction``` value based on the ```unit_of_measurement``` of the sensor and the used datasource. The unit of measurement of the datasource can be found in the readme of the datasource.
      The different corrections are described in the script.
    - Determine the ```cutoff_new_meter``` and ```cutoff_invalid_value``` values based on the unit of measurement of the target sensor. The different cutoffs are described in the script.
- Execute the SQL and wait for it to complete. (Please be patient because this can take some time!)
- Commit the changes by selecting "Write changes" in the toolbar, if the script ends without errors. In case of an error select ```Revert changes``` and correct the error and execute the script again.

#### Replace Home Assistant database
- Make sure that the Home Assistant core is still stopped (Home Assistant UI does not respond)
- Upload ```home-assistant_v2.db``` to the Home Assistant ```config``` directory (For example: use WinSCP in combination with the Home Assistant SSH addon). 
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the ```reboot``` command)
- Validate the imported data in the ```Energy Dashboard```
- Enjoy :-)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
