import os, sys, datetime
import pandas as pd

def generateImportDataFile(dataFrame, outputFile, filterColumn):
    # Create file the file
    print('Creating file: ' + outputFile);
    dataFrameFiltered = dataFrame.filter(['Datum', filterColumn])
    dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)

def generateImportDataFiles(path, inputFileName):

    inputFile = path + os.sep + inputFileName
    if os.path.exists(inputFile):
        print('Found file: ' + inputFile)

        _, inputFileNameExtension = os.path.splitext(inputFileName);
        if (inputFileNameExtension == '.xlsx'):
            print('Opening input XLSX data')
            # Open the specified file
            # Second row contains header so skip the first row
            dataFrame = pd.read_excel(inputFile, decimal = ',', skiprows = 1, parse_dates = ['Datum'])
        
            print('Loading data');
            # Define start and end date
            startDate = '01-01-1970'
            endDate = '31-12-2099'
            dataFrame = dataFrame.loc[(dataFrame['Datum'] >= datetime.datetime.strptime(startDate, '%d-%m-%Y')) & (dataFrame['Datum'] <= datetime.datetime.strptime(endDate, '%d-%m-%Y'))]
    
            # Transform the date into unix timestamp for Home-Assistant
            dataFrame['Datum'] = (dataFrame['Datum'].view('int64') / 1000000000).astype('int64')
            
            # Create file: elec_feed_in_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_in_tariff_1_high_resolution.csv', 'Meterstand hoogtarief (El 2)')

            # Create file: elec_feed_in_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_in_tariff_2_high_resolution.csv', 'Meterstand laagtarief (El 1)')

            # Create file: elec_feed_out_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_out_tariff_1_high_resolution.csv', 'Meterstand hoogtarief (El 4)')

            # Create file: elec_feed_out_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_out_tariff_2_high_resolution.csv', 'Meterstand laagtarief (El 3)')   

            print('Done')
        else:
            print('Only .xlsx files are supported')
    else:
        print('Could not find file: ' + inputFile)
        

if __name__ == '__main__':
    print('Eneco Data Prepare');
    print('');
    print('This python script prepares Eneco data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(os.getcwd(), sys.argv[1])
    else:
        print('EnecoPrepareData usage:')
        print('EnecoPrepareData <Eneco xlsx filename>')
