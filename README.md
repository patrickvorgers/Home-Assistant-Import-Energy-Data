# HA-Import-Toon-Data
Import historical Toon energy data into Home Assistant so that it can be used in the Energy Dashboard.

I have been enjoying the Home Assistant Energy Dashboard feature since it came out. The only downside was that I could not import my historical Toon (Eneco) data which I was using until the Home Assistant Energy Dashboard came out. This SQL script solves that issue and makes it possbile to import historical exported data from Toon into Home Assistant. It adds the statistics data that is missing in Home Assistant and adjusts the existing data.

**Latest data still correct after import (short_term_statistics work)**
![2023](https://user-images.githubusercontent.com/10108665/230038379-8d20d264-c49e-4c98-b1f6-241942306886.JPG)

**Data of 2019 (imported from Toon using hourly interval data - statistics work)**
![2019](https://user-images.githubusercontent.com/10108665/230038399-61886f6c-ba39-4343-8b96-0fb779b39ba2.JPG)

**Data of 2015 (imported from Toon using day interval data - statistics work)**
![2015](https://user-images.githubusercontent.com/10108665/230038421-3833847a-79a4-40a2-8937-2b5f2ae3f3cc.JPG)


**How to:**
- Download and install: DB Browser for SQLite https://sqlitebrowser.org/ (tested windows version 3.12.2)
- Download and install/configure: WinSCP (https://winscp.net/eng/download.php)
- Backup and download Toon data  (Instellingen -> Internet -> Toon data)
- Backup and download Home Assistant data
	- Disable recorder while making the backup -> Developer tools/Services/Call service: Recorder:disable
- Stop the Home Assistant core (Developer tools/Services/Call service: Home Assistant Core Integration: Stop)
- Toon data: "export.zip"
	- Extract: "usage.zip"
- Toon data: "usage.zip"
	- Extract: "elec_quantity_nt_orig_CurrentElectricityQuantity_5yrhours.csv"
 	- Extract: "elec_quantity_lt_orig_CurrentElectricityQuantity_5yrhours.csv"
	- Extract: "elec_quantity_nt_produ_CurrentElectricityQuantity_5yrhours.csv"
	- Extract: "elec_quantity_lt_produ_CurrentElectricityQuantity_5yrhours.csv"
	- Extract: "elec_solar_quantity_CurrentElectricityQuantity_5yrhours.csv"
	- Extract: "elec_quantity_nt_orig_CurrentElectricityQuantity_10yrdays.csv"
	- Extract: "elec_quantity_lt_orig_CurrentElectricityQuantity_10yrdays.csv"
	- Extract: "elec_quantity_nt_produ_CurrentElectricityQuantity_10yrdays.csv"
	- Extract: "elec_quantity_lt_produ_CurrentElectricityQuantity_10yrdays.csv"
	- Extract: "elec_solar_quantity_CurrentElectricityQuantity_10yrdays.csv"
	- Extract: "gas_quantity_CurrentGasQuantity_5yrhours.csv"
	- Extract: "gas_quantity_CurrentGasQuantity_10yrdays.csv"
- Home Assistant data: 
	- Extract: "home-assistant_v2.db" (from "backup.tar" extract "homeassistant.tar.gz" from "data" folder). As an alternative it is also possible to download the "home-assistant_v2.db" directly from the Home Assistant "config" directory (For example: use WinSCP in combination with the Home Assistant SSH addon). In case of this method make sure to make a copy of the database so that you can always restore this version of the database.
- Start "DB Browser for SQLite"
- Open project "Toon.sqbpro".
	- If the database is not loaded directly you have to open the "home-assistant_v2.db" database manually ("Open Database").
- Validate the schema version of the database (Browse Data -> Table: schema_version)
	- The script has been tested with schema version 35 . With higher versions you should validate if the structure of the "statistics" and "short_term_statistics" tables have changed.
	- Used fields in table "statistics": metadata_id, state, sum, start_ts, created_ts
	- Used fields in table "short_term_statistics": sum 
- Import, one at a time, all the extracted Toon data elec* and gas* files (File -> Import -> Table from CSV file...)
  	- It is possible to load data from multiple Toons (for example: Toon 1 and Toon 2). The exported files from the second Toon can be imported into the existing tables. You have to create the table manually (field1, field2) in case a Toon file does not contain any data (0 KB). The name of the table should be the name of the file without ".csv", another option is to comment out the SQL for the specific file.
- Lookup in the "statistics_meta" table the ID's of the sensors (Browse Data -> Table: statistics_meta; You can use "filter" to find the id of the sensor)
	- Below are the sensors you need to find. The names are the default names from the Home Assistant Toon integration.
  ```
	id	statistic_id					source		unit_of_measurement
	2	sensor.gas_meter				recorder	m³
	3	sensor.electricity_meter_feed_in_tariff_1	recorder	kWh
	4	sensor.electricity_meter_feed_in_tariff_2	recorder	kWh
	6	sensor.electricity_meter_feed_out_tariff_1	recorder	kWh
	7	sensor.electricity_meter_feed_out_tariff_2	recorder	kWh
	10	sensor.solar_energy_produced_today		recorder	kWh
- Change the SQL script and insert the correct ID on the places where the text "* Change *" has been added in the SQL statement.
	- The script basically has the same SQL statements for each sensor so in case a sensor is not needed you can comment out that specific part (for example: solar, gas)
- Execute the SQL and wait for it to complete.
- Commit the changes by selecting "Write changes" in the toolbar, if the script ends without errors. In case of an error select "Revert changes" and correct the error and execute this step again.
- Upload "home-assistant_v2.db" to the Home Assistant "config" directory (For example: use WinSCP in combination with the Home Assistant SSH addon). 
- Restart/reboot Home Assistant (physically reboot Home Assistant or login using PUTTY-SSH and execute the "reboot" command)
- Validate the imported Toon data in the "Energy Dashboard"
- Enjoy :-)
