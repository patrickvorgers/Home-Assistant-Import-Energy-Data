# Energy provider: Enphase

Enphase offers the option to export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (hour interval) - kWh (Metered version)
- Electricity production - Tariff 1 - High resolution (hour interval) - kWh (Metered version)
- Solar production - High resolution (hour interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**
- Export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site
  - Go to the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) site
  - Set the language to English (bottom right corner)
  - Login with your account
  - Follow the below substeps in case you have access to the installer version of the site (orange layout)
    - Select your system
    - In the site menu select 'MyEnphase View'
    - Go to the new tab that has been opened with the 'customer' view (blue layout)
  - Select the 'Hamburger icon' in the top right corner (three lines)
  - Select 'System'
  - Select 'Reports'
  - In the top dropdown select 'Custom' (scroll down in the dropdown to find the report)
  - Select the data type: 'Produced' and if available 'Imported/Exported' (Metered version)
  - Choose the data frequency: 1 hour
  - Fill in the start and end date of the report and press 'Email Report'
  - After the report has been generated the CSV is emailed to the registerd emailadress
  - Open the email and download the generated CSV file to your PC
- Download the ```EnphaseDataPrepare.py``` file and put it in the same directory as the Enphase data
- Execute the python script with as parameter the name of the file that contains the exported data ```python EnphaseDataPrepare.py 9999999_site_energy_production_report.csv```. The python script creates the needed files for the generic import script.
- Follow the steps in the overall how-to