# Energy provider: Eneco (Toon)

Eneco (Toon) offers the option to export the below data from the Toon device. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval)
- Electricity consumption - Tariff 1 - Low resolution (day interval)
- Electricity consumption - Tariff 2 - High resolution (hour interval)
- Electricity consumption - Tariff 2 - Low resolution (day interval)
- Electricity production - Tariff 1 - High resolution (hour interval)
- Electricity production - Tariff 1 - Low resolution (day interval)
- Electricity production - Tariff 2 - High resolution (hour interval)
- Electricity production - Tariff 2 - Low resolution (day interval)
- Solar production - High resolution (hour interval)
- Solar production - Low resolution (day interval)
- Gas consumption - High resolution (hour interval)
- Gas consumption - Low resolution (day interval)

**How-to:**
- Backup and download Toon data (Instellingen -> Internet -> Toon data)
- Download the ```Toon prepare data.bat``` file and put it in the same directory as the downloaded Toon data ```export.zip```
- Execute on Windows the ```Toon prepare data.bat``` file. The script extracts the needed files and creates the needed files for the generic import script. 
- Follow the steps in the overall how-to