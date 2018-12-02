import os
from glob import glob
from subprocess import call

# generic link for downloading data
# just replace years
# https://www.oceancolour.org/thredds/wcs/CCI_ALL-v3.0-DAILY?service=WCS&version=1.0.0&request=GetCoverage&crs=OGC%3ACRS84&format=NetCDF3&coverage=chlor_a&bbox=-10.151%2C-20.83%2C14.897%2C7.207&time=2011-12-31T23%3A59%3A59.384Z%2F2013-12-31T23%3A59%3A59.181Z

# remove last time layer in the file (it duplicates with the next file)
# and keep time of the start
oc_files = glob('/home/antonk/Downloads/WCS*.nc')
for oc_file in oc_files:
    cmd = 'ncea -O -d time,,-2 %s %s' % (oc_file, os.path.basename(oc_file))
    print(cmd)
    #call(cmd, shell=True)
    cmd = 'ncks -O --mk_rec_dmn time %s %s' % (os.path.basename(oc_file), os.path.basename(oc_file))
    print(cmd)
    #call(cmd, shell=True)

# get starting time from all files
oc_files = glob('WCS*.nc')
time0s = []
for oc_file in oc_files:
    ds = Dataset(oc_file)
    time = ds['time'][:].data
    print(os.path.basename(oc_file), time[0], time[-1])
    time0s.append(time[0])

# create command to concatenate files
cmd = 'ncrcat -h '
for oc_file in np.array(oc_files)[np.argsort(time0s)]:
    print(oc_file)
    cmd += oc_file + ' '
cmd += ' /Data/sat/downloads/OCCCI/occci_angola_chlor_a_19980101-20151231.nc'
print(cmd)
call(cmd, shell=True)

