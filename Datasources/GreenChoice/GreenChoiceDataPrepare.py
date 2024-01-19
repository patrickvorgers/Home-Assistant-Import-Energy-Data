from ast import parse
import os, sys, datetime
import pandas as pd

def generateImportDataFile(dataFrame, outputFile, filterColumn):
    # Create file the file
    print('Creating file: ' + outputFile);
    dataFrameFiltered = dataFrame.filter(['OpnameDatum', filterColumn])
    dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)

def generateImportDataFiles(path, inputFileName):

    inputFile = path + os.sep + inputFileName
    if os.path.exists(inputFile):
        print('Found file: ' + inputFile)
        
        _, inputFileNameExtension = os.path.splitext(inputFileName);
        if (inputFileNameExtension == '.csv'):
            print('Opening input CSV data')
            # Open the specified file 
            dataFrame = pd.read_csv(inputFile, sep = ';', decimal = '.', parse_dates = ['OpnameDatum'])
        
            print('Loading data');
            # Define start and end date
            startDate = '01-01-1970'
            endDate = '31-12-2099'
            dataFrame = dataFrame.loc[(dataFrame['OpnameDatum'] >= datetime.datetime.strptime(startDate, '%d-%m-%Y')) & (dataFrame['OpnameDatum'] <= datetime.datetime.strptime(endDate, '%d-%m-%Y'))]
    
            # Transform the date into unix timestamp for Home-Assistant
            dataFrame['OpnameDatum'] = (dataFrame['OpnameDatum'].view('int64') / 1000000000).astype('int64')

            # Create file: elec_feed_in_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_in_tariff_1_high_resolution.csv', 'StandNormaal')

            # Create file: elec_feed_in_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_in_tariff_2_high_resolution.csv', 'StandDal')

            # Create file: elec_feed_out_tariff_1_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_out_tariff_1_high_resolution.csv', 'TerugleveringNormaal')

            # Create file: elec_feed_out_tariff_2_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_feed_out_tariff_2_high_resolution.csv', 'TerugleveringDal')            
        
            print('Done')
        else:
            print('Only .csv files are supported')
    else:
        print('Could not find file: ' + inputFile)
        

if __name__ == '__main__':
    print('GreenChoice Data Prepare');
    print('');
    print('This python script prepares GreenChoice data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(os.getcwd(), sys.argv[1])
    else:
        print('GreenChoicePrepareData usage:')
        print('GreenChoicePrepareData <GreenChoice csv filename>')
