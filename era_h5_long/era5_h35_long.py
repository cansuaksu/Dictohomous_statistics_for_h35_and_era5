'''THIS CODE BELOW IS FOR OBTAINING THE COUNT OF DICHOTOMOUS METRICS SUCH AS HITS, MISSES, FALSE ALARMS AND CORRECT NEGATIVES AND
FOR EACH PIXEL AND FOR AVAILABLE H35 FILES IN 2019'''

from osgeo import gdal
import glob
import cv2
import os
import h5py
import numpy as np
import datetime
from datetime import timedelta
from logger import Logger

logger = Logger('era_h5') # For debug & compile time

#This is to get a date list, because h35 and ERA5 files both have dates in their names, and the comparison of h35 and era5 should be
#done within the same date.

start = datetime.datetime.strptime("20190101", "%Y%m%d")
end = datetime.datetime.strptime("20191231", "%Y%m%d")
dateList = [start + timedelta(n) for n in range(int((end - start).days) + 1)]
# date_list = [i.strftime('%Y-%m-%d') for i in dateList]
date_list = [i.strftime('%Y%m%d') for i in dateList]

# Process paths for ERA5 and h35 products:
process_path = 'E:/era5_snowdepth/h35_products/'
process_path2 = 'E:/era5_snowdepth/era5_sn/'
#
# #for h35 make a dataframe with the dates
#
H5_files = [file_ for file_ in glob.glob1(process_path, "*.h5")]

output_array = np.zeros([5,360, 720])
checklist_date = [] # H35 is not available on every date of 2019. This list contains the dates that h35 are available on.
for date_ in date_list:
    match = list(filter(lambda x: x.find(date_) != -1, H5_files))
    if len(match) > 0:
        checklist_date.append(date_)
    else:
        pass


def resize_h5(date_): #H35 is not the same size with ERA5 files, so H35 is resampled by this function.
    h5 = 'h35_' + date_ + '_day_TSMS.h5'
    hf_h35 = h5py.File(os.path.join(process_path, h5), 'r')

    data_h35 = hf_h35['fsc']
    f2 = np.array(data_h35)

    return cv2.resize(f2, dsize=(720, 360), interpolation=cv2.INTER_NEAREST)


#ERA5 file (NETCDF) was turned to rasters beforehand.

def read_era5(date_):
    date2 = (datetime.datetime.strptime(date_, '%Y%m%d')).strftime('%Y-%m-%d')
    era5 = 'era5_' + date2 + '.tif'
    era5_f = os.path.join(process_path2, era5)
    era5_f = gdal.Open(era5_f)
    f = era5_f.ReadAsArray()
    return f

# ERA5 and H35 do not have the same meridian start (ERA5 is (0,360) and H35 is (-180,180). To solve this, some arrangements were made in below
#function (like j+360 or j-360 in ERA5 files) so that ERA5 files are also (-180,180), and the corresponding H35 pixels are in the same location.


def check(i,j,f2,f,output_array): #The check for hits, misses etc. is done by this function.
    if j < 360:
        if 50 <= f2[i, j] <= 100 and f[i, j + 360] > 2:
            output_array[0,i,j] += 1 #HITS
        elif f2[i, j] < 50 and f[i, j + 360] > 2:
            output_array[1,i,j] += 1 #MISSES
        elif 50 <= f2[i, j] <= 100 and f[i, j + 360] < 2:
            output_array[2, i, j] += 1 #FALSE ALARMS
        elif f2[i, j] < 50 and f[i, j + 360] < 2:
            output_array[3,i,j] += 1 # CORRECT NEGATIVES
        else:
            output_array[4,i,j] +=1 #THIS IS FOR NO DATA
    elif j > 360:
        if 50 <= f2[i, j] <= 100 and f[i, j - 360] > 2:
            output_array[0,i,j] += 1 #HITS
        elif f2[i, j] < 50 and f[i, j - 360] > 2:
            output_array[1,i,j] += 1 #MISSES
        elif 50 <= f2[i, j] <= 100 and f[i, j - 360] < 2:
            output_array[2, i, j] += 1 #FALSE ALARMS
        elif f2[i, j] < 50 and f[i, j - 360] < 2:
            output_array[3,i,j] += 1 # CORRECT NEGATIVES
        else:
            output_array[4, i, j] += 1 #THIS IS FOR NO DATA



def modify_outputs(output_array, date_):
    try:
        logger.log_info('reading era5 file.')
        f = read_era5(date_)
        logger.log_info('reading h5 file.')
        f2 = resize_h5(date_)
        logger.log_info('procecssing pixels.')
        for i in range(360):  # -> y
            for j in range(720):  # -> x
                check(i,j,f2,f,output_array)
                logger.log_info(f'checked {date_}')
    except:
        pass

for date_ in checklist_date:
    logger.log_info(f'file with date: {date_} has been started')
    modify_outputs(output_array, date_)
np.save("thedata.npy", output_array)

