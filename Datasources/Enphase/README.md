# Energy provider: Enphase

Enphase offers the option to export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) website. This data can be transformed and used to import into Home Assistant.

**Data provided**
- Solar production - High resolution (day interval) - Wh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**
- Export data from the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) website
    - **Energy production (Envoy standard & Envoy metered)**
        - Go to the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) website
        - Set the language to English (bottom right corner)
        - Login with your account
        - Select your system
        - Select the 'Reports' tab
        - In the 'Select Report' dropdown select the 'Site Energy Production' report
        - Fill in the start and end date of the report and press 'Submit'
        - After the report has been generated press the button with the arrow down (tooltip: CSV)
        - The data is now downloaded to your PC
    - **Energy production & Grid import & Grid export (Envoy metered)**
        - Go to the [Enlighten Enphase Energy](https://enlighten.enphaseenergy.com/) website
        - Set the language to English (bottom right corner)
        - Login with your account
        - Select your system
        - Select the 'Reports' tab
        - In the 'Select Report' dropdown select the 'Custom' report
        - Select the data type: Produced, Imported/Exported
        - Choose the data frequency: 1 hour
        - Fill in the start and end date of the report and press 'Email Report'
        - After the report has been generated the CSV is emailed to the registerd emailadress
        - Open the email and download the generated CSV file to your PC
- Download the ```EnphaseDataPrepare.py``` or ```EnphaseDataPrepare (battery).py``` file and put it in the same directory as the Enphase data. Use the ```EnphaseDataPrepare (battery).py``` file in case the exported file uses ```Energy Delivered (Wh)``` as energy columnname.
- Execute the python script with as parameter the name of the file that contains the exported data ```python EnphaseDataPrepare.py 9999999_site_energy_production_report.csv```. The python script creates the needed file for the generic import script.
- Follow the steps in the overall how-to