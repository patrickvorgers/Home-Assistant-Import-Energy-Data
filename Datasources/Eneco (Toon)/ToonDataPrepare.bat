@echo off
REM Script for preparing the exported Toon data so that it can be used by the import script.
REM requires Windows 10 or up

echo Toon Data Prepare
echo:
echo This windows script prepares Toon data for import into Home Assistant.
echo Make sure that the export.zip file is in the current directory.
echo The files will be prepared in the current directory any previous files will be overwritten!
echo:

:choice
set /P answerContinue=Are you sure you want to continue[Y/N]?
if /I "%answerContinue%" EQU "Y" goto :_process
if /I "%answerContinue%" EQU "N" goto :_terminate
goto :choice


:_process
REM Start processing
echo:
echo Data preparation started
if exist Export.zip (
  echo Found file export.zip

  echo Extracting usage.zip from export.zip
  tar -xf .\export.zip usage.zip

  echo Extracting CSV files from usage.zip
  tar -xf .\usage.zip elec_quantity_lt_orig* elec_quantity_lt_produ* elec_quantity_nt_orig* elec_quantity_nt_produ* elec_solar_quantity* gas_quantity*

  echo Removing extracted usage.zip
  del .\usage.zip

  echo Removing any old CSV files
  del elec_feed_in_tariff_1_high_resolution.csv >NUL 2>NUL
  del elec_feed_in_tariff_1_low_resolution.csv >NUL 2>NUL
  del elec_feed_in_tariff_2_high_resolution.csv >NUL 2>NUL
  del elec_feed_in_tariff_2_low_resolution.csv >NUL 2>NUL
  del elec_feed_out_tariff_1_high_resolution.csv >NUL 2>NUL
  del elec_feed_out_tariff_1_low_resolution.csv >NUL 2>NUL
  del elec_feed_out_tariff_2_high_resolution.csv >NUL 2>NUL
  del elec_feed_out_tariff_2_low_resolution.csv >NUL 2>NUL
  del elec_solar_high_resolution.csv >NUL 2>NUL
  del elec_solar_low_resolution.csv >NUL 2>NUL
  del gas_high_resolution.csv >NUL 2>NUL
  del gas_low_resolution.csv >NUL 2>NUL

  echo Renaming extracted CSV files
  rename elec_quantity_nt_orig_CurrentElectricityQuantity_5yrhours.csv elec_feed_in_tariff_1_high_resolution.csv
  rename elec_quantity_nt_orig_CurrentElectricityQuantity_10yrdays.csv elec_feed_in_tariff_1_low_resolution.csv
  rename elec_quantity_lt_orig_CurrentElectricityQuantity_5yrhours.csv elec_feed_in_tariff_2_high_resolution.csv
  rename elec_quantity_lt_orig_CurrentElectricityQuantity_10yrdays.csv elec_feed_in_tariff_2_low_resolution.csv
  rename elec_quantity_nt_produ_CurrentElectricityQuantity_5yrhours.csv elec_feed_out_tariff_1_high_resolution.csv
  rename elec_quantity_nt_produ_CurrentElectricityQuantity_10yrdays.csv elec_feed_out_tariff_1_low_resolution.csv
  rename elec_quantity_lt_produ_CurrentElectricityQuantity_5yrhours.csv elec_feed_out_tariff_2_high_resolution.csv
  rename elec_quantity_lt_produ_CurrentElectricityQuantity_10yrdays.csv elec_feed_out_tariff_2_low_resolution.csv
  rename elec_solar_quantity_CurrentElectricityQuantity_5yrhours.csv elec_solar_high_resolution.csv
  rename elec_solar_quantity_CurrentElectricityQuantity_10yrdays.csv elec_solar_low_resolution.csv
  rename gas_quantity_CurrentGasQuantity_5yrhours.csv gas_high_resolution.csv
  rename gas_quantity_CurrentGasQuantity_10yrdays.csv gas_low_resolution.csv

  echo Done
) else (
  echo Error: Could not find file export.zip in the current directory.
  goto _terminate
)

goto _terminate

:_terminate
REM No action needed