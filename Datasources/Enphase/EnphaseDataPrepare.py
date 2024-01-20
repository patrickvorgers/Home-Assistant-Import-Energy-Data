import os, sys, datetime
import pandas as pd

def prepareData(dataFrame):
    print('Preparing data');

    # Define start and end date
    df = dataFrame.loc[(dataFrame['Date/Time'] >= datetime.datetime.strptime('01-01-1970', '%d-%m-%Y')) & (dataFrame['Date/Time'] <= datetime.datetime.strptime('31-12-2099', '%d-%m-%Y'))]
    # Transform the date into unix timestamp for Home-Assistant
    df['Date/Time'] = (df['Date/Time'].view('int64') / 1000000000).astype('int64')
    
    # Clean up the value column by removing the string quotes and locale indicator
    df['Energy Produced (Wh)'] = df['Energy Produced (Wh)'].str.replace(",", "").replace('"', '').astype(int)
    
    # Make the value column increasing 
    for index in range(1, len(dataFrame)):
        if index > 1:
            df.loc[index, 'Energy Produced (Wh)'] = df.loc[index - 1, 'Energy Produced (Wh)'] + df.loc[index, 'Energy Produced (Wh)']
    return df


def generateImportDataFile(dataFrame, outputFile, filterColumn):
    # Create file the file
    print('Creating file: ' + outputFile);
    dataFrameFiltered = dataFrame.filter(['Date/Time', filterColumn])
    dataFrameFiltered.to_csv(outputFile, sep = ',', decimal = '.', header = False, index = False)


def generateImportDataFiles(path, inputFileName):

    inputFile = path + os.sep + inputFileName
    if os.path.exists(inputFile):
        print('Found file: ' + inputFile)
        
        _, inputFileNameExtension = os.path.splitext(inputFileName);
        if (inputFileNameExtension == '.csv'):
            print('Loading CSV data');
            # Open the specified file
            # First row contains header so we don't have to skip rows, last row contains totals so we have to skip the footer. This is only supported by the 'python' engine
            dataFrame = pd.read_csv(inputFile, sep = ',', decimal = '.', skiprows = 0, skipfooter = 1, parse_dates = ['Date/Time'], date_format = '%m/%d/%Y', engine='python')
            
            # Prepare the data
            dataFrame = prepareData(dataFrame)
  
            # Create file: elec_solar_high_resolution.csv
            generateImportDataFile(dataFrame, path + os.sep + 'elec_solar_high_resolution.csv', 'Energy Produced (Wh)')
        
            print('Done')
        else:
            print('Only .csv files are supported')
    else:
        print('Could not find file: ' + inputFile)
        

if __name__ == '__main__':
    print('Enphase Data Prepare');
    print('');
    print('This python script prepares Enphase data for import into Home Assistant.')
    print('The files will be prepared in the current directory any previous files will be overwritten!')
    print('')
    if len(sys.argv) == 2:
        if input('Are you sure you want to continue [Y/N]?: ').lower().strip()[:1] == 'y':
            generateImportDataFiles(os.getcwd(), sys.argv[1])
    else:
        print('EnphasePrepareData usage:')
        print('EnphasePrepareData <Enphase csv filename>')