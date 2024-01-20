import os, sys, datetime
import pandas as pd

def prepareData(dataFrame):
    print('Preparing data');

    # Define start and end date
    df = dataFrame.loc[(dataFrame['Date Time UTC'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['Date Time UTC'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]
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


def generateImportDataFiles(path, inputFileName):

    inputFile = path + os.sep + inputFileName
    if os.path.exists(inputFile):
        print('Found file: ' + inputFile)

        _, inputFileNameExtension = os.path.splitext(inputFileName);
        if (inputFileNameExtension == '.xlsx'):
            print('Loading XLSX data');
            # Open the specified file
            # First row contains header so we don't have to skip rows, last row does not contain totals so we do not have to skip the footer
            dataFrame = pd.read_excel(inputFile, decimal = ',', skiprows = 0, skipfooter = 0, parse_dates = ['Date Time UTC'])
        
            # Prepare the data
            dataFrame = prepareData(dataFrame)

            # Create file: elec_feed_in_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_in_tariff_1_high_resolution.csv', False, True)

            # Create file: elec_feed_out_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_out_tariff_1_high_resolution.csv', False, False)

            # Create file: gas_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'gas_high_resolution.csv', True, True)

            print('Done')
        else:
            print('Only .xlsx files are supported')
    else:
        print('Could not find file: ' + inputFile)
        

if __name__ == '__main__':
    print('NextEnergy Data Prepare');
    print('');
    print('This python script prepares NextEnergy data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(os.getcwd(), sys.argv[1])
    else:
        print('NextEnergyPrepareData usage:')
        print('NextEnergyPrepareData <NextEnergy xlsx filename>')
