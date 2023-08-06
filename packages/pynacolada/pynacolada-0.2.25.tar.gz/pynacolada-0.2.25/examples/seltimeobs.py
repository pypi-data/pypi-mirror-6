import pynacolada as pcd
import numpy as np
import datetime as dt
from scipy.interpolate import interp1d
from Scientific.IO import NetCDF
import os

from numpy import *
import sciproc as sp
#from sciproc import tsfill

# purpose: get netcdf data for user-specified time range in an efficient way and write it back to another netcdf file (example script)

# our new time-range with convenient fixed timespacing.
datetimes_new = sp.dtrange(dt.datetime(2009,1,1),dt.datetime(2009,12,31,23),dt.timedelta(hours=1))

# nc met originele variabelenamen
fn ='/media/URB_1/archive/profiles_belgium/mol_sck/dbo_Meteo'
# # nc met profiel 
fn ='/media/URB_1/archive/profiles_belgium/mol_sck/dbo_Meteo_2'

ncfile = NetCDF.NetCDFFile(fn+'.nc','r')
ncfile_seltime = NetCDF.NetCDFFile(fn+'_sel_maffie.nc','w')

datetimes_orig = pcd.ncgetdatetime(ncfile)
# selidx = np.array(cosel(dtsprf,dts),dtype=int)


# seconds of original the netcdf file relative to its first timestep. We need this because interpol1d can't manage datetime objects.
seconds_orig= [(dt - datetimes_orig[0]).total_seconds() for dt in datetimes_orig]

# also seconds for the new netcdf file, please... (relative to the first timestep of the original ncfile of course.)
seconds_new= [(dt - datetimes_orig[0]).total_seconds() for dt in datetimes_new]

# we do time interpolation for all variables except the dimensions
for varnc in ncfile.variables:
    if varnc not in ncfile.dimensions:
        pcd.pcd(\
                lambda x: interp1d(seconds_orig,x,kind='linear',axis=0)(seconds_new), # our function we want to apply on the netcdf \
                ('time',), # in this case, the operation is on the time coordinate \
                [{'file': ncfile, 'varname':varnc}], # input file specification \
                [{'file': ncfile_seltime, 'varname': varnc}], # output file specification \
                appenddim=True, # makes the operation faster for multidimensional data\
                maxmembytes=10**9,  # but set a limit on the memory buffer (not really an issue here) \
               )

# write the new time-coordinate to the new netcdffile
pcd.ncwritedatetime(ncfile_seltime,datetimes_new,tunits='hours',refdat=datetimes_new[0])
ncfile_seltime.close(); print ('data written to:',ncfile_seltime )
ncfile.close()




