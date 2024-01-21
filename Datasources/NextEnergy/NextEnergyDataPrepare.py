import os, sys, datetime, glob
import pandas as pd

def prepareData(dataFrame):
    print('Preparing data');

    # Select only correct dates
    df = dataFrame.loc[(dataFrame['Date Time UTC'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['Date Time UTC'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]

    # Make sure that the data is correctly sorted
    df.sort_values(by = 'Date Time UTC', ascending = True, inplace = True)

    # Transform the date into unix timestamp for Home-Assistant
    df['Date Time UTC'] = (df['Date Time UTC'].view('int64') / 1000000000).astype('int64')

    return df


def generateImportDataFile(dataFrame, outputFile, isGas, isConsumption):
    # Create file the file
    print('Creating file: ' + outputFile);
    dataFrameFiltered = dataFrame[dataFrame['Unit'] == 'm3'] if isGas else dataFrame[dataFrame['Unit'] != 'm3']
    dataFrameFiltered = dataFrameFiltered[dataFrameFiltered['Direction'] == 'levering'] if isConsumption else dataFrameFiltered[dataFrameFiltered['Direction'] != 'levering']
    dataFrameFiltered = dataFrameFiltered.filter(['Date Time UTC', 'Reading Start'])
    dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)


def fileRead(inputFileName):
    # Read the specified file
    print('Loading data: ' + inputFileName)
    
    # First row contains header so we don't have to skip rows, last row does not contain totals so we do not have to skip the footer
    df = pd.read_excel(inputFileName, decimal = ',', skiprows = 0, skipfooter = 0)
    df['Date Time UTC'] = pd.to_datetime(df['Date Time UTC'], format = '%d-%m-%Y %H:%M:%S')
    
    return df


def correctFileExtensions(fileNames):
    # Check all filenames for the right extension
    for fileName in fileNames:
        _, fileNameExtension = os.path.splitext(fileName);
        if (fileNameExtension != '.xlsx'):
            return False
    return True


def generateImportDataFiles(inputFileNames):
    # Find the file(s)
    fileNames = glob.glob(inputFileNames)
    if len(fileNames) > 0:
        print('Found files based on: ' + inputFileNames)
        # Check if all the found files are of the correct type
        if correctFileExtensions(fileNames):
            # Read all the found files and concat them
            dataFrame = pd.concat(map(fileRead, fileNames), ignore_index = True, sort = True)
        
            # Prepare the data
            dataFrame = prepareData(dataFrame)

            # Create file: elec_feed_in_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_feed_in_tariff_1_high_resolution.csv', False, True)

            # Create file: elec_feed_out_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_feed_out_tariff_1_high_resolution.csv', False, False)

            # Create file: gas_high_resolution.csv
            generateImportDataFile(dataFrame, 'gas_high_resolution.csv', True, True)

            print('Done')
        else:
            print('Only .xlsx datafiles are allowed');    
    else:
        print('No files found based on : ' + inputFileNames)
       

if __name__ == '__main__':
    print('NextEnergy Data Prepare');
    print('');
    print('This python script prepares NextEnergy data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(sys.argv[1])
    else:
        print('NextEnergyPrepareData usage:')
        print('NextEnergyPrepareData <NextEnergy .xlsx filename (wildard)>')
