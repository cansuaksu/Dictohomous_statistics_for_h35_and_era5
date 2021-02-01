'''THIS CODE BELOW IS FOR OBTAINING THE COUNT OF DICHOTOMOUS METRICS SUCH AS HITS, MISSES, FALSE ALARMS AND CORRECT NEGATIVES AND
FOR EACH PIXEL AND FOR AVAILABLE H35 FILES IN 2019 IN SNOW SEASON'''
import pandas as pd
from osgeo import gdal
import glob
import cv2
import os
import h5py
import numpy as np
import datetime
from datetime import timedelta
from logger import Logger
import matplotlib.pyplot as plt

logger = Logger('era_h5') # For debug & compile time
""
#This is to get a date list, because h35 and ERA5 files both have dates in their names, and the comparison of h35 and era5 should be
#done within the same date.

start_day = datetime.datetime.strptime("20190101", "%Y%m%d")
end_day = datetime.datetime.strptime("20191231", "%Y%m%d")
date_list = [start_day + timedelta(n) for n in range(int((end_day - start_day).days) + 1)]
df = pd.DataFrame({'date': date_list})
df['month'] = pd.DataFrame(df['date'].dt.month)

# df_ = df.loc[(df['month'] == 12) | (df['month'] == 1) | (df['month'] == 2) | (df['month']== 3) | (df['month'] == 4)]
datelist = pd.to_datetime(df['date']).dt.date.to_list()


# Process paths for ERA5 and h35 products:
process_path2 = 'E:/era5_snowdepth/era5_sn/'
process_path = 'E:/h35/'
# #
# # #for h35 make a dataframe with the dates
# #
H5_files = [file_ for file_ in glob.glob1(process_path, "*.tif")]


 # H35 is not available on every date of 2019. This list contains the dates that h35 are available on.


def checklist(month):
    checklist_date = []
    pd_ = df.loc[df['month']==month] #1,2,3,4,5
    datelist = pd.to_datetime(pd_['date']).dt.date.to_list()

    for date_ in datelist:
        date2 = date_.strftime('%Y%m%d')

        # a = (datetime.datetime.strptime(date2, '%Y-%m%d')).strftime('%Y%m%d')
        match = list(filter(lambda x: x.find(date2) != -1, H5_files))
        if len(match) > 0:
            checklist_date.append(date2)

        else:
            pass
    return checklist_date
def read_h35(date_):#H35 is not the same size with ERA5 files, so H35 is resampled by this function.
    # date_ = date_.strftime('%Y%m%d')
    h5 = 'h35_' + date_ + '_day_TSMS.tif'
    h5= os.path.join(process_path, h5)
    h5 = gdal.Open(h5)
    f = h5.ReadAsArray()
    return f

# #ERA5 file (NETCDF) was turned to rasters beforehand.

def read_era5(date_):
    # date_ = date_.strftime('%Y%m%d')
    date2 = (datetime.datetime.strptime(date_, '%Y%m%d')).strftime('%Y-%m-%d')
    era5 = 'era5_' + date2 + 'r.tif'
    era5_f = os.path.join(process_path2, era5)
    era5_f = gdal.Open(era5_f)
    f2 = era5_f.ReadAsArray()

    im = cv2.resize(f2, dsize=(36000, 18050), interpolation=cv2.INTER_NEAREST)
    im = im[24:9023,0:35999]
    return im

'''BU MONTLY DE YAPILACAK'''
monthlist = [1,2,3,4,5]
checklist_date= []
for month in monthlist:
    a = checklist(month)
    checklist_date.append(a)

flat_list = [item for sublist in checklist_date for item in sublist]


df5 = pd.DataFrame(columns=['Date','Hits','False Alarms','Misses','Correct Negatives','POD','FAR','Accuracy'])
columns=['Date','Hits','False Alarms','Misses','Correct Negatives','POD','FAR','Accuracy']
data = []
flat_list = ['20190201','20190202']


for date_ in flat_list:
    logger.log_info(f'working on date {date_}')
    f= read_h35(date_)
    im= read_era5(date_)
    data_h35 = np.where((f > 100), 255, f)
    data_h35_zero = np.where((data_h35 < 50), 0, data_h35)
    data_h35_final = np.where(np.logical_and(data_h35_zero != 0, data_h35_zero != 255), 1, data_h35_zero)
    data_era5 = np.where((im < 0.10), 0, 1)

#daily
    A = np.where((data_era5 == 1) & (data_h35_final == 1), 1, 0)
    B = np.where((data_era5 == 0) & (data_h35_final == 1), 1, 0)
    C = np.where((data_era5 == 1) & ( data_h35_final == 0), 1, 0)
    D = np.where((data_era5 == 0) & (data_h35_final == 0), 1, 0)

    a = np.sum(A)
    b = np.sum(B)
    c = np.sum(C)
    d = np.sum(D)

    pod = a / (a + c)
    far = b / (a + b)
    acc = (a + d) / (a + b + c + d)



    values = [date_, a, b, c, d, pod, far, acc]
    zipped = zip(columns, values)
    a_dictionary = dict(zipped)
    data.append(a_dictionary)

# #the whole month
#
#     # A_whole += np.where(np.logical_and(data_era5 == 1, data_h35_final == 1), 1, 0)
#     # B_whole += np.where(np.logical_and(data_era5 == 0, data_h35_final == 1), 1, 0)
#     # C_whole += np.where(np.logical_and(data_era5 == 1, data_h35_final == 0), 1, 0)
#     # D_whole += np.where(np.logical_and(data_era5 == 0, data_h35_final == 0), 1, 0)
#
df5 = df5.append(data, True)
df5.to_csv('5monthmetrics_try2.csv')

# plt.imshow(A)
# plt.show()

# np.save('hits_january.npy',A_whole)
# np.save('false-alarms_january.npy',B_whole)
# np.save('misses_january.npy',C_whole)
# np.save('correct_negatives_january.npy',D_whole)
