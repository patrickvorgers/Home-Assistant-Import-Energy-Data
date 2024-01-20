# Energy provider: Eneco (Toon)

Eneco (Toon) offers the option to export data from the Toon device. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - Wh
- Electricity consumption - Tariff 1 - Low resolution (day interval) - Wh
- Electricity consumption - Tariff 2 - High resolution (hour interval) - Wh
- Electricity consumption - Tariff 2 - Low resolution (day interval) - Wh
- Electricity production - Tariff 1 - High resolution (hour interval) - Wh
- Electricity production - Tariff 1 - Low resolution (day interval) - Wh
- Electricity production - Tariff 2 - High resolution (hour interval) - Wh
- Electricity production - Tariff 2 - Low resolution (day interval) - Wh
- Solar production - High resolution (hour interval) - Wh
- Solar production - Low resolution (day interval) - Wh
- Gas consumption - High resolution (hour interval) - m³
- Gas consumption - Low resolution (day interval) - m³

**How-to:**
- Backup and download Toon data
	- On the Toon device goto: Instellingen -> Internet -> Toon data
	- Press 'Maak kopie'
	- After completion, download the data via the provided link on the Toon device
- Download the ```ToonDataPrepare.bat``` file and put it in the same directory as the downloaded Toon data ```export.zip```
- Execute on Windows the ```ToonDataPrepare.bat``` file. The script extracts the needed files and creates the needed files for the generic import script. 
- Follow the steps in the overall how-to