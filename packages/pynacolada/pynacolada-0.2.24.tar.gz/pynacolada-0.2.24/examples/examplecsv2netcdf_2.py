import numpy as np
import datetime as dt
from Scientific.IO import NetCDF
import pynacolada as pcd

csvfile = open('./data/example2.csv','r')
ncfile = NetCDF.NetCDFFile('./data/example2.nc','w')
pcd.csv2netcdf(csvfile,ncfile,formatlist=[[np.int32,np.nan]]*2+[['daytime','dayssince']],readcolnames=False,refdat=dt.datetime(2011,1,1),customnames=['bla','blabla',],nalist=['-999.0'])

csvfile.close()
ncfile.close(); print('data written to', ncfile)


