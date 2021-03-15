from typing import Dict, List
import pygrib
import numpy as np
from os import walk, environ
from tqdm import tqdm
import pandas as pd
import json
from mail import Email
from time import sleep

# script to get the average rain max rain and min rain for areas defined in areas.json file from GRIB files

# the path at which the GRIB directories live
PATH = 'omar_data/'
OUTPUT_FILE = 'rain_data.xlsx'
try:
    with open('areas.json') as f:
        AREAS = json.load(f)['areas']
except FileNotFoundError: 
    raise BaseException('could not process areas.json file make sure that areas.json exists')
except KeyError:
    raise BaseException('areas key is not specified in areas.json')


# init the Email
try:
    sender_address = environ['EMAIL_ADDRESS']
    receiver_address = environ['EMAIL_ADDRESS']
    sender_pass = environ['PASSWORD']
except KeyError as e:
    print('please make sure that you set the environment variables EMAIL_ADDRESS and PASSWORD correctly')
    raise

email = Email(sender_address, receiver_address, sender_pass)

print('found {} areas in areas.json file'.format(len(AREAS)))
print('---------------------------------')


def _get_files_dirs(path: str) -> List[str]:
    '''
        get all the files in a directory path
        :param path:    path to the files or directories
        :return:        list of files, list of direcotries in the path
    '''
    f = []
    dirs = []
    for (_, dirnames, filenames) in walk(path):
        f.extend(filenames)
        dirs.extend(dirnames)
        break
    return f, dirs


def get_inst_rain_average(file_path: str) -> Dict[str, float]:
    '''
        function to get the average rain over a grid for locations specified in areas.json 
        :param file_path x:   file path to a grib file 
        :return:              data row including (name: area name, area_max: max rain, 
                                area_min: min rain, area_average: average rain for all
                                areas specified in areas.json file)
    '''
    grbs = pygrib.open(file_path)
    grb = grbs[1]
    data_row = {}
    date_time = str(grb)[-12:]
    data_row['time'] = date_time
    for area in AREAS:
        # get data for each area
        data, lon, lat = grb.data(lon1=area['lon1'], lon2=area['lon2'], lat1=area['lat1'], lat2=area['lat2'])
        average = np.average(data) # average over the whole grid
        data_row[area['name'] + '_average'] = average
        data_row[area['name'] + '_min'] = min(data)
        data_row[area['name'] + '_max'] = max(data)
    print(data_row)
    return data_row
    
def get_rain_excel_data():
    def _send_email(progress, total):
            message = '''message from the server:
            the current progress from the server is {} over {}, find the
            attached updated rain data file
            '''.format(progress, total)
            tries = 10 # sometimes the smtp server fails to establish a connection to send an email
            for i in range(tries):
                try:
                    email.send_mail(message, 'update rain data file', OUTPUT_FILE)
                    break
                except:
                    print('attempting to send an email, attempt number {}/{}'.format(i + 1, tries))
                    sleep(5)
                    continue

            if i >= 9:
                print('could not send an email')

    def _update_dataframe_file(data_rows):
        try:
            df = pd.read_excel(OUTPUT_FILE, index_col=0)
            for row in data_rows:
                df = df.append(row, ignore_index=True)
            df.to_excel(OUTPUT_FILE)
            print('successfully updated the excel file!')
        except FileNotFoundError:
            # initialize the df
            df = pd.DataFrame(columns=[key for key in data_rows[0]])

            for row in data_rows:
                df = df.append(row, ignore_index=True)
            df.to_excel(OUTPUT_FILE)  
            print('successfully created the excel file!')

    _, dirs = _get_files_dirs(PATH)
    for directory in dirs:
        print('processing directory {} out of {}'.format(dirs.index(directory) + 1, len(dirs)))
        directory_path = PATH + directory
        files, _ = _get_files_dirs(directory_path)
        # Iterate over all the grib files in the directory path
        with tqdm(total=len(files)) as t:
            data_rows = []
            for i in range(len(files)):
                file = files[i]
                file_path = '{}/{}'.format(directory_path, file)
                data_row = get_inst_rain_average(file_path)
                data_rows.append(data_row)
                if i % 50 == 0 or i == len(files):
                    _update_dataframe_file(data_rows)
                    _send_email(i + 1, len(files))
                    data_rows = []
                    
                print(data_row)
                t.update(1)


if __name__ == "__main__":
    # main entry point
    get_rain_excel_data()
