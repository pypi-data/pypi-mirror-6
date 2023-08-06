import pynacolada as pcd
import numpy as np
import datetime as dt
from Scientific.IO import NetCDF
import os

import sciproc as sp



# purpose: put vertical mast observation profiles at Zwijndrecht (VMM) properly into a netcdf file, also accounting for the local-time coordinate


csvfile = open('./data/example3.csv','r')
ncfile = NetCDF.NetCDFFile('./data/example3.nc','w')

pcd.csv2netcdf(csvfile,ncfile,sep=',',formatlist=[[dt.datetime,'%m/%d/%Y %H:%M:%S']]+[[np.double,np.nan]]*15,refdat=dt.datetime(2000,1,1,0,0), tunits='hours')
ncfile.close(); print 'data written to: ',ncfile


