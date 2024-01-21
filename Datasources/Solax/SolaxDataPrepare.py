import os, sys, datetime, glob
import pandas as pd


def prepareData(dataFrame):
    print('Preparing data');

    # Select only correct dates
    df = dataFrame.loc[(dataFrame['Time'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['Time'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]

    # Make sure that the data is correctly sorted
    df.sort_values(by = 'Time', ascending = True, inplace = True)

    # Transform the date into unix timestamp for Home-Assistant
    df['Time'] = (df['Time'].view('int64') / 1000000000).astype('int64')
    
    # Make the value column increasing (skip first row)
    for index in range(1, len(dataFrame)):
        df.loc[index, 'PV Yield Energy (kWh)'] = round(df.loc[index - 1, 'PV Yield Energy (kWh)'] + df.loc[index, 'PV Yield Energy (kWh)'], 1)
            
    return df


def generateImportDataFile(dataFrame, outputFile, filterColumn):
    # Create file the file
    print('Creating file: ' + outputFile);
    dataFrameFiltered = dataFrame.filter(['Time', filterColumn])
    dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)


def fileRead(inputFileName):
    # Read the specified file
    print('Loading data: ' + inputFileName)
    
    # Fourth row contains header so we have to skip 3 rows, last row does not contain totals so we do not have to skip the footer
    df = pd.read_excel(inputFileName, decimal = ',', skiprows = 3, skipfooter = 0)
    df['Time'] = pd.to_datetime(df['Time'], format = '%Y-%m-%d')
    
    return df


def correctFileExtensions(fileNames):
    # Check all filenames for the right extension
    for fileName in fileNames:
        _, fileNameExtension = os.path.splitext(fileName);
        if (fileNameExtension != '.xls'):
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

            # Create file: elec_solar_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_solar_high_resolution.csv', 'PV Yield Energy (kWh)')

            print('Done')
        else:
            print('Only .xls datafiles are allowed');    
    else:
        print('No files found based on : ' + inputFileNames)
        

if __name__ == '__main__':
    print('Solax Data Prepare');
    print('');
    print('This python script prepares Solax data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(sys.argv[1])
    else:
        print('SolaxPrepareData usage:')
        print('SolaxPrepareData <Solax .xls filename (wildcard)>')
