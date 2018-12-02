import datetime as dt

import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt

from zoning import fill_gaps_nn

#
ifilename = '/Data/sat/downloads/OCCCI/occci_angola_chlor_a_19980101-20151231.nc'

ds1 = Dataset(ifilename)
time1 = ds1['time'][:].data
lat1 = ds1['lat'][::-1].data
lon1 = ds1['lon'][:].data
chlor_a1 = ds1['chlor_a'][:, ::-1, :].data
date10 = dt.datetime(1970,1,1)
res1 = 4
#lon1_grd, lat1_grd = np.meshgrid(lon1, lat1)

lays1, rows1, cols1  = chlor_a1.shape
lon2col = lambda lon: int(round((cols1 - 1) * (lon - lon1[0]) / (lon1[-1] - lon1[0])))
lat2row = lambda lat: int(round((rows1 - 1) * (lat - lat1[0]) / (lat1[-1] - lat1[0])))

for ofilename in ['cycloniceddies.nc', 'anticycloniceddies.nc']:
    ds2 = Dataset(ofilename)
    y2 = ds2['year'][:].data.astype(int)
    m2 = ds2['month'][:].data.astype(int)
    d2 = ds2['day'][:].data.astype(int)
    time2 = np.array([(dt.datetime(yy,mm,dd) - date10).days for yy,mm,dd in zip(y2,m2,d2)], dtype=float)
    lon2 = ds2['lon'][:].data
    lat2 = ds2['lat'][:].data
    rad2 = ds2['Radius'][:].data

    gpi = ((lat2 > lat1.min()) * (lon2 > lon1.min()) * (time2 > time1.min()) *
           (lat2 < lat1.max()) * (lon2 < lon1.max()) * (time2 < time1.max()))
    idx2 = np.where(gpi)[0]

    chl2 = np.zeros(len(y2), dtype=[('mean',float), ('median',float), ('std', float), ('disk_size', int), ('sample_size', int)])
    for ii2, ti2, lo2, la2, ra2 in zip(idx2, time2[gpi], lon2[gpi], lat2[gpi], rad2[gpi]):
        time1i = np.where(ti2 == time1)[0]
        if len(time1i) > 0:
            time1i = time1i[0]
        r2 = lat2row(la2)
        c2 = lon2col(lo2)
        w2 = int(ra2/res1)
        sub_chla1 = chlor_a1[time1i, (r2 - w2):(r2 + w2 + 1), (c2 - w2):(c2 + w2 + 1)]
        if sub_chla1.shape != (w2*2+1,)*2:
            continue
        disk = np.hypot(*np.meshgrid(*[range(-w2,(w2+1))]*2)) <= w2
        disk_size = len(disk[disk])
        gpi_disk = disk * np.isfinite(sub_chla1)
        sample_size = len(gpi_disk[gpi_disk])
        if sample_size > 0:
            chl2['mean'][ii2] = np.mean(sub_chla1[gpi_disk])
            chl2['median'][ii2] = np.median(sub_chla1[gpi_disk])
            chl2['std'][ii2] = np.std(sub_chla1[gpi_disk])
            chl2['disk_size'][ii2] = disk_size
            chl2['sample_size'][ii2] = sample_size
            print(ofilename[0], y2[ii2], m2[ii2], d2[ii2], chl2[ii2])


    np.savez(ofilename + '.npz', chlor_a=chl2)
