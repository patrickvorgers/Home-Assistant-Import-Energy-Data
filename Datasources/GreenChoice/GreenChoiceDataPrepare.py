import os, sys, datetime, glob
import pandas as pd
from collections import namedtuple


DataFilter = namedtuple('DataFilter', ['column', 'value', 'equal'])


def prepareData(dataFrame):
    print('Preparing data');

    # Select only correct dates
    df = dataFrame.loc[(dataFrame['OpnameDatum'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['OpnameDatum'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]
    
    # Make sure that the data is correctly sorted
    df.sort_values(by = 'OpnameDatum', ascending = True, inplace = True)

    # Transform the date into unix timestamp for Home-Assistant
    df['OpnameDatum'] = (df['OpnameDatum'].view('int64') / 1000000000).astype('int64')

    return df


def filterData(dataFrame, filters):
    df = dataFrame
    for dataFilter in filters:
        df = df[df[dataFilter.column] == dataFilter.value] if dataFilter.equal else df[df[dataFilter.column] != dataFilter.value]

    return df


def recalculateData(dataFrame, dataColumn):
    df = dataFrame
    
    # Make the value column increasing (skip first row)
    previousRowIndex = -1
    for index, _ in df.iterrows():
        if previousRowIndex > -1:
            # Add the value of the previous row to the current row
            df.at[index, dataColumn] = round(df.at[index, dataColumn] + df.at[previousRowIndex, dataColumn], 3)
        previousRowIndex = index
        
    return df


def generateImportDataFile(dataFrame, outputFile, dataColumn, filters, recalculate):
    # Check if the column exists
    if dataColumn in dataFrame.columns:
        # Create file the file
        print('Creating file: ' + outputFile);
        dataFrameFiltered = filterData(dataFrame, filters)
        if recalculate:
            dataFrameFiltered = recalculateData(dataFrameFiltered, dataColumn)
        dataFrameFiltered = dataFrameFiltered.filter(['OpnameDatum', dataColumn])
        dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)
    else:
        print('Could not create file: ' + outputFile + ' because column: ' + dataColumn + ' does not exist')


def fileRead(inputFileName):
    # Read the specified file
    print('Loading data: ' + inputFileName)
    
    # First row contains header so we don't have to skip rows, last row does not contain totals so we do not have to skip the footer
    df = pd.read_csv(inputFileName, sep = ';', decimal = '.', skiprows = 0, skipfooter = 0)
    df['OpnameDatum'] = pd.to_datetime(df['OpnameDatum'], format = '%Y-%m-%d')
    # Remove the timezone (if it exists)
    df['OpnameDatum'] = df['OpnameDatum'].dt.tz_localize(None)
    
    return df


def correctFileExtensions(fileNames):
    # Check all filenames for the right extension
    for fileName in fileNames:
        _, fileNameExtension = os.path.splitext(fileName);
        if (fileNameExtension != '.csv'):
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
            generateImportDataFile(dataFrame, 'elec_feed_in_tariff_1_high_resolution.csv', 'StandNormaal', [], False)

            # Create file: elec_feed_in_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_feed_in_tariff_2_high_resolution.csv', 'StandDal', [], False)

            # Create file: elec_feed_out_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_feed_out_tariff_1_high_resolution.csv', 'TerugleveringNormaal', [], False)

            # Create file: elec_feed_out_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, 'elec_feed_out_tariff_2_high_resolution.csv', 'TerugleveringDal', [], False)

            print('Done')
        else:
            print('Only .csv datafiles are allowed');    
    else:
        print('No files found based on : ' + inputFileNames)


if __name__ == '__main__':
    print('GreenChoice Data Prepare');
    print('');
    print('This python script prepares GreenChoice data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(sys.argv[1])
    else:
        print('GreenChoicePrepareData usage:')
        print('GreenChoicePrepareData <GreenChoice .csv filename (wildcard)>')