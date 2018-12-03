import os
from shutil import copyfile
import numpy as np
from netCDF4 import Dataset

long_names = {
'mean' : 'Mean chlorophyll concentration in eddie, ug/l',
'median' : 'Median chlorophyll concentration in eddie, ug/l',
'std' : 'Standard deviation of chlorophyll concentration in eddie, ug/l',
'disk_size' : 'Total number of pixels in eddie',
'sample_size' : 'Number of valid pixels',
}

for ifilename in ['cycloniceddies.nc', 'anticycloniceddies.nc']:
    ofilename = ifilename.replace('.nc', '_chl.nc')
    # crated dataset for update
    copyfile(ifilename, ofilename)
    # open chl in eddies
    chl = np.load(ifilename + '.npz')['chlor_a']
    # open dataset for update
    ds = Dataset(ofilename, 'a')

    for name in chl.dtype.names:
        nc_name = 'chl_' + name
        print(nc_name)
        ds.createVariable(nc_name, '<f8', 'entries')
        ds[nc_name][:] = chl[name]
        ds[nc_name].long_name = long_names[name]

    ds.close()
