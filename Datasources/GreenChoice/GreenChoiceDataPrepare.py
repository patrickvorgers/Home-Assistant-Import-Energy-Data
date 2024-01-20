import os, sys, datetime
import pandas as pd

def prepareData(dataFrame):
    print('Preparing data');

    # Define start and end date
    df = dataFrame.loc[(dataFrame['OpnameDatum'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['OpnameDatum'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]
    
    # Transform the date into unix timestamp for Home-Assistant
    df['OpnameDatum'] = (df['OpnameDatum'].view('int64') / 1000000000).astype('int64')
    return df


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
            print('Loading CSV data');
            # Open the specified file
            # First row contains header so we don't have to skip rows, last row does not contain totals so we do not have to skip the footer
            dataFrame = pd.read_csv(inputFile, sep = ';', decimal = '.', skiprows = 0, skipfooter = 0, parse_dates = ['OpnameDatum'], date_format = '%Y-%m-%d')
 
            # Prepare the data
            dataFrame = prepareData(dataFrame)

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
