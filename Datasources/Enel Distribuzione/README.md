# Energy provider: Enel Distribuzione

Enel Distribuzione, part of the Italian grid authority, allows users to export their electricity consumption data, which can be processed and imported into Home Assistant.

**Data provided**
- Electricity consumption - Tariff 1 - High resolution (15-minute interval) - kWh

**Tooling needed**
- Python 3
- Pandas python library ```pip install pandas```

**How-to**
- Export your electricity consumption data from the Enel Distribuzione website (Italian grid authority).
- Download the ```EnelDistribuzioneDataPrepare.py``` script and place it in the same directory as the exported Enel Distribuzione data.
- Execute the Python script by providing the name of the exported file as a parameter. Example:  
  ```python EnelDistribuzioneDataPrepare.py ExportData_*.csv```.  
  The script will generate the necessary files for importing the data into Home Assistant.
- Follow the steps in the overall Home Assistant import guide for integrating the data into your setup.