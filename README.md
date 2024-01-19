<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data">
    <img src="https://raw.githubusercontent.com/patrickvorgers/Home-Assistant-Import-Energy-Data/main/Images/Logo.png" alt="Logo" width="80" height="80">
  </a>

<h1 align="center">Home Assistant Import Historical Energy Data</h1>

  <p align="center">
Import historical energy data from external datasources into Home Assistant so that it can be used in the Energy Dashboard.
    <br />
    <br />
    <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues">Report Bug</a>
    ·
    <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#authors">Authors</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a name="about-the-project"></a>
## About The Project

![2019](https://user-images.githubusercontent.com/10108665/230038399-61886f6c-ba39-4343-8b96-0fb779b39ba2.JPG)

### Background

I have been enjoying the Home Assistant Energy Dashboard feature since it came out. The only downside was that I could not import my historical energy data. I was using "Toon" from my Dutch energyprovider Eneco until the Home Assistant Energy Dashboard came out. This led me to write an import script that could import Toon data into Home Assistant. After I got it working I made this specific import script as is available on GitHub.

Since then the script has been used and adapted by several people so it could be used with other energy providers. Their feedback led me to the idea to rewrite my initial script and make it more generic and robust so that it can be used easier with other energy providers. The latest version of the script makes it possbile to import historical exported energy data  into Home Assistant. It adds the statistics data that is missing in Home Assistant and adjusts the existing data.

**Latest data still correct after import (short_term_statistics work)**
![2023](https://user-images.githubusercontent.com/10108665/230038379-8d20d264-c49e-4c98-b1f6-241942306886.JPG)
</br></br>
**Data of 2019 - Imported using high resolution interval data (hourly) - statistics work**
![2019](https://user-images.githubusercontent.com/10108665/230038399-61886f6c-ba39-4343-8b96-0fb779b39ba2.JPG)
</br></br>
**Data of 2015 - Imported using low resolution interval data (daily) - statistics work**
![2015](https://user-images.githubusercontent.com/10108665/230038421-3833847a-79a4-40a2-8937-2b5f2ae3f3cc.JPG)

### Features:
<ul>
    <li>Imports correctly historical energy data into Home Assistant</li>
    <li>Supports combination of low and high resolution data</li>
    <li>Supports electrical feed in, electrical feed out, solar power and gas data</li>
    <li>Supports data feeds with double tariffs (normal tariff / low tariff)</li>
    <li>One line configuration in case a sensor is not needed</li>
    <li>Possibility to provide a conversion factor per sensor (for instance conversion between Wh and kWh)</li>
    <li>Supports reset of sensors (for instance replacement of energy meter) </li>
</ul>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
<a name="getting-started"></a>
## Getting Started

### Disclaimer

Importing historical energy data into Home Assistant is not simple and requires some technical knowledge. It alters the database of Home Assistant so be sure that you <b>always</b> have a recent backup of your Home Assistant data!

<a name="How-to"></a>
### How-to

#### Tooling
- Download and install: DB Browser (64 bit) for SQLite https://sqlitebrowser.org/ (tested windows version 3.12.2)
- Download and install/configure: WinSCP (https://winscp.net/eng/download.php)

#### Source data preparation
- Check whether a script/how-to exists for your provider (datasources directory)
    - Script/how-to exists:
	    - Follow how-to to prepare the needed CSV files
    - Script/How-to does not exist:
	    - Determine how to get the data from your energy provider (download/API etc.)
		- Get the data from the energy provider using the identified method
		- Convert the data in the needed CSV files. The definition for the CSV files is very simple. Each row contains: Epoch Unix Timestamp, sensor value
		    - Example:
		        - 1540634400, 8120605
		        - 1540638000, 8120808
		        - 1540641600, 8120993
		        - 1540645200, 8121012
		- Depending on the used sensors determine which CSV data files need to be created:
		    - ```elec_feed_in_tariff_1_high_resolution.csv```
			    - Contains the highest resolution usage data available (for instance: hour resolution)
				- Used in case there is only one tariff
			- ```elec_feed_in_tariff_1_low_resolution.csv```
				- Contains the lowest resolution usage data available (for instance: day resolution)
				- Used in case there is only one tariff
				- Not needed in case that there is only one resolution available.
			- ```elec_feed_in_tariff_2_high_resolution.csv```
				- Contains the highest resolution usage data available (for instance: hour resolution)
				- Not needed in case that there is only one tariff available.
		    - ```elec_feed_in_tariff_2_low_resolution.csv```
				- Contains the lowest resolution usage data available (for instance: day resolution)
				- Not needed in case that there is only one tariff available.
				- Not needed in case that there is only one resolution available.
			- ```elec_feed_out_tariff_1_high_resolution.csv```
				- Contains the highest resolution production data available (for instance: hour resolution)
				- Used in case there is only one tariff
				- Not needed in case that there is no production (for instance: no solar panels, no battery export)
			- ```elec_feed_out_tariff_1_low_resolution.csv```
				- Contains the lowest resolution production data available (for instance: day resolution).
				- Used in case there is only one tariff
				- Not needed in case that there is no production (for instance: no solar panels, no battery export)
				- Not needed in case that there is only one resolution available.
			- ```elec_feed_out_tariff_2_high_resolution.csv```
				- Contains the highest resolution production data available (for instance: hour resolution).
				- Not needed in case that there is no production (for instance: no solar panels, no battery export)
				- Not needed in case that there is only one tariff available.
			- ```elec_feed_out_tariff_2_low_resolution.csv```
				- Contains the lowest resolution production data available (for instance: day resolution).
				- Not needed in case that there is no production (for instance: no solar panels, no battery export)
				- Not needed in case that there is only one tariff available.
				- Not needed in case that there is only one resolution available.
			- ```elec_solar_high_resolution.csv```
				- Contains the highest resolution production data available (for instance: hour resolution)
				- Not needed in case that there are no solar panels
			- ```elec_solar_low_resolution.csv```
				- Contains the lowest resolution production data available (for instance: day resolution)
				- Not needed in case that there are no solar panels
				- Not needed in case that there is only one resolution available.
			- ```gas_high_resolution.csv```
				- Contains the highest resolution production data available (for instance: hour resolution).
				- Not needed in case that there is no gas usage
			- ```gas_low_resolution.csv```
				- Contains the lowest resolution production data available (for instance: day resolution).
				- Not needed in case that there is no gas usage
				- Not needed in case that there is only one resolution available.

#### Home Assistant preparation
- Create a backup of the Home Assistant database
    - Disable recorder while making the backup -> Developer tools/Services/Call service: Recorder:disable
- Download the created backup
- Stop the Home Assistant core
    - Developer tools/Services/Call service: Home Assistant Core Integration: Stop
- Home Assistant data: 
    - extract: ```home-assistant_v2.db``` (from ```backup.tar``` extract ```homeassistant.tar.gz``` from ```data``` folder). As an alternative it is also possible to download the ```home-assistant_v2.db``` directly from the Home Assistant ```config``` directory (For example: use WinSCP in combination with the Home Assistant SSH addon). In case of this method make sure that you didn't skip the step to create a backup so that you can always restore this version of the database!

#### Import the data
- Start ```DB Browser for SQLite```
- Open project ```Import Energy data into Home Assistant.sqbpro```.
    - If the database is not loaded directly you have to open the ```home-assistant_v2.db``` database manually ("Open Database").
- Validate the schema version of the database (Browse Data -> Table: schema_version)
    - The script has been tested with schema version 42. With higher versions you should validate if the structure of the ```statistics``` and ```short_term_statistics``` tables have changed.
        - Used fields in table ```statistics```: ```metadata_id```, ```state```, ```sum```, ```start_ts```, ```created_ts```
        - Used fields in table ```short_term_statistics```: ```sum```
- Import, one at a time, all the created CSV data ```elec*``` and ```gas*``` files (File -> Import -> Table from CSV file...)
    - It is possible to load data from multiple CSV's with the same name. The data of the second import is than added to the existing tables. This can be used in case there are multiple energy source providers for different timeperiods. In this case you first import the files from the first energy provider and than then second etc.
- Lookup in the ```statistics_meta``` table the ID's of the sensors (Browse Data -> Table: statistics_meta; You can use "filter" to find the id of the sensor)
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
```
- Change the script and remove/comment out the lines of the sensors that are not needed. They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement.
- Change the script and update the ID's according to the found ID's in the ```statistics_meta``` table.
  They can be found at the top of the script by looking up the lines where ```/* Change */``` has been added in the SQL statement. Determine also the correction factor in case the ```unit_of_measurement``` of the sensor differs from the used datasource. The unit of measurement of the datasource can be found in the readme of the datasource.
- Execute the SQL and wait for it to complete. (Please be patient because this can take some time!)
- Commit the changes by selecting "Write changes" in the toolbar, if the script ends without errors. In case of an error select ```Revert changes``` and correct the error and execute the script again.

#### Replace Home Assistant database
- Make sure that the Home Assistant core is still stopped (Home Assistant UI does not respond)
- Upload ```home-assistant_v2.db``` to the Home Assistant ```config``` directory (For example: use WinSCP in combination with the Home Assistant SSH addon). 
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the ```reboot``` command)
- Validate the imported data in the ```Energy Dashboard```
- Enjoy :-)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Authors -->
<a name="authors"></a>
## Authors

The project initially began as a tool for importing historical data for Toon (Eneco) into Home Assistant. In early 2024, the project scope expanded, enabling the import of data from various energy providers.

Hopefully, together with the community, the number of supported energy providers (datasources) can be expanded. Making it easier to import data from various energy providers.

Please share scripts or how-to guides if you have built an integration with a new energy provider. Your name will be added to the list below as a contributor.

### Project technical leads:

* Patrick Vorgers (the Netherlands)

### All other contributors:

* Nick de Wijer (https://github.com/ndewijer)
    * Initial implementation: GreenChoice

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
<a name="roadmap"></a>
## Roadmap

- [ ] Support more datasources
- [ ] Support MariaDB or provide workaround 

See the [open issues](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
<a name="contact"></a>
## Contact

Project Link: [https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/patrickvorgers/SPC.svg?style=for-the-badge
[issues-url]: https://github.com/patrickvorgers/SPC/issues
