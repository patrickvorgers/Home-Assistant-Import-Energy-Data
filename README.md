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

[![GitHub Release][releases-shield]][releases]
[![Issues][issues-shield]][issues-url]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data">
    <img src="https://raw.githubusercontent.com/patrickvorgers/Home-Assistant-Import-Energy-Data/main/Images/Logo.png" alt="Logo" width="80" height="80">
  </a>

<h1 align="center">Home Assistant Import Historical Energy Data</h1>

  <p align="center">
Import historical energy/water data from external datasources into Home Assistant so that it can be used in the Energy Dashboard.
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
    <li><a href="#contributions">Contributions</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
<a name="about-the-project"></a>
## About The Project

![2019](https://user-images.githubusercontent.com/10108665/230038399-61886f6c-ba39-4343-8b96-0fb779b39ba2.JPG)

### Background

I have been enjoying the Home Assistant Energy Dashboard feature since it came out. The only downside was that I could not import my historical energy/water data. I was using "Toon" from my Dutch energyprovider Eneco until the Home Assistant Energy Dashboard came out. This led me to write an import script that could import Toon data into Home Assistant. After I got it working I made this specific import script as is available on GitHub.

Since then the import script has been used and adapted by several people so it could be used with other energy providers. Their feedback led me to the idea to rewrite my initial script and make it more generic and robust so that it can be used easier with other energy providers. The latest version of the script is independent from the energy provider and makes it possbile to import historical exported energy data into Home Assistant. It adds the statistics data that is missing in Home Assistant and adjusts the existing data.

The generic import script requires the data to be in a specific simple CSV file format (```Epoch Unix Timestamp```, ```sensor value```). For several energy providers conversion scripts exist that convert the energy provider specific format to the needed format. To make live easier a generic conversion script is available that can handle formats like CSV, XLS, XLSX and JSON and can deal with headers, footers, date formats, data filtering and data recalculation.

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
    <li>Imports correctly historical energy and water data into Home Assistant</li>
    <li>Supports combination of low and high resolution data</li>
    <li>Supports electrical feed in, electrical feed out, solar power, gas and water data</li>
    <li>Supports data feeds with double tariffs (normal tariff / low tariff)</li>
    <li>One line configuration in case a sensor is not needed</li>
    <li>Possibility to provide a conversion factor per sensor (for instance conversion between Wh/kWh or L/m³)</li>
    <li>Supports reset of sensors (for instance replacement of energy meter)</li>
    <li>Support for SQLite (standard Home Assistant database) and MariaDB</li>
    <li>Generic data conversion script for "unsupported" energy providers</li>
    <li>Growing list of data conversion scripts for different energy providers (most using generic data conversion script)</li>
</ul>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
<a name="getting-started"></a>
## Getting Started

### Disclaimer

Importing historical energy data into Home Assistant is not simple and requires some technical knowledge. It alters the database of Home Assistant so be sure that you <u><b>always</b></u> have a recent backup of your Home Assistant data!

<a name="How-to"></a>
### How-to

#### Source data preparation
- Check whether a script/how-to exists for your provider (datasources directory)
    - Script/how-to exists:
	    - Follow how-to to prepare the needed CSV files
    - Script/How-to does not exist:
	    - Determine how to get the data from your energy provider (download/API etc.)
		- Get the data from the energy provider using the identified method
		- Convert the data in the needed CSV files. The generic data conversion script ```TemplateDataPrepare.py``` can be used in most cases. In case the CSV files are created manually the CSV files should follow the following simple definition where each row contains: ```Epoch Unix Timestamp```, ```sensor value```
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
			- ```water_high_resolution.csv```
				- Contains the highest resolution production data available (for instance: hour resolution).
				- Not needed in case that there is no water usage
			- ```water_low_resolution.csv```
				- Contains the lowest resolution production data available (for instance: day resolution).
				- Not needed in case that there is no water usage
				- Not needed in case that there is only one resolution available.

#### Database
- Determine the type of database that the Home Assistant installation uses and continue with that specific how-to. The standard installation of Home Assistant uses SQLite.
    - [SQLite how-to](SQLite) 
	- [MariaDB how-to](MariaDB)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Authors -->
<a name="authors"></a>
## Authors

The project initially began as a tool for importing historical data for Toon (Eneco) into Home Assistant. In early 2024, the project scope expanded, enabling the import of data from various energy providers.

Hopefully, together with the community, the number of supported energy providers (datasources) can be expanded. Making it easier to import data from various energy providers.

Please share scripts or how-to guides if you have built an integration with a new energy provider. Your name will be added to the list below as a contributor.

### Project technical leads:

* Patrick Vorgers (the Netherlands)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Contributions -->
<a name="contributions"></a>
## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)
### All contributors:

* Nick de Wijer (https://github.com/ndewijer)
    * Initial implementation: GreenChoice
	* Sample files for: SolarEdge
* vGelder (https://github.com/vGelder)
    * Sample files for: Oxxio
    * Sample files for: Liander
    * Sample files for: Engie
* Jaap P. (https://github.com/AJediIAm)
    * Implementation: P1Mon (ZTATZ)
* Minze Tolsman (https://github.com/miezie)
    * Implementation: VanOns

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
<a name="roadmap"></a>
## Roadmap

- [ ] Support more datasources
- [X] Support MariaDB or provide workaround 

See the [open issues](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
<a name="contact"></a>
## Contact

Project Link: [https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data](https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[buymecoffee]: https://www.buymeacoffee.com/patrickvorgers
[buymecoffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
[commits-shield]: https://img.shields.io/github/commit-activity/y/patrickvorgers/Home-Assistant-Import-Energy-Data.svg?style=for-the-badge
[commits]: https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/commits/main
[issues-shield]: https://img.shields.io/github/issues/patrickvorgers/Home-Assistant-Import-Energy-Data.svg?style=for-the-badge
[issues-url]: https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/issues
[license-shield]: https://img.shields.io/github/license/patrickvorgers/Home-Assistant-Import-Energy-Data.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-patrickvorgers-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/patrickvorgers/Home-Assistant-Import-Energy-Data.svg?style=for-the-badge
[releases]: https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data/releases

