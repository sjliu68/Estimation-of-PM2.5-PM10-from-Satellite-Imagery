# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 21:36:57 2019

@author: SJ

Calculate AOD from satellite imagery using the 6S model

"""

import numpy as np
import pickle
import scipy
import gdal
import matplotlib.pyplot as plt
import time
from sklearn.ensemble import RandomForestRegressor


#%%
# model created from a look-up table
# NOTICE: depends on the wavelength !!!
fpath = r'F:\t0823\iLUTs\LANDSAT_OLI_B2.ilut'

# Environment condition setups
sz = 60 # solar zentith, could be different for each pixel
wv = 5 # water vapour, estimated from http://images.remss.com/cdr/climate_data_record_browse.html
o3 = 0.3 # ozone, estimated from https://ozoneaq.gsfc.nasa.gov/missions
km = 0.2 # altitude in kilometers, check from Google Earth

year = 2019
month = 3
day = 31


#%%
# open the model
with open(fpath,"rb") as ilut_file:
    iLUT = pickle.load(ilut_file)
   
# arguments in the model
''' 
solar zentith [degrees] (0 - 75)
water vapour [g/m2] (0 - 8.5)
ozone [cm-atm] (0 - 0.8)
aerosol optical thickness [unitless] (0 - 3)
surface altitude [km] (0 - 7.75)
'''

#%%
# correct the parameters for atmospheric correction based on day of years
def corr_ab(a,b,doy):
    elliptical_orbit_correction = 0.03275104*np.cos(doy/59.66638337) + 0.96804905
    a *= elliptical_orbit_correction
    b *= elliptical_orbit_correction
    return a,b

def date2day(year,month,day):
    year = int(year)
    month = int(month)
    day = int(day)
    out = day
    days = [31,28,31,30,31,30,31,31,30,31,30,31]
    i = 0
    if (year%4 == 0 and year%100 != 0) or (year%400 == 0):
        days[1] = 29
    while i< month-1:
        out += days[i]
        i+=1
    print('date:',year,month,day,'day:',out)
    return out

#%% day of year
doy = date2day(year,month,day) # day of years, extract from satellite data

#%% New look-up table to check radiance
Ls = np.arange(0,300,0.1) # range from 0-300 should be quite enough
gofaot = 0.005
aots = np.arange(0.00,2.0,gofaot) # aod range from 0-3, it should be enough when ranged from 0-2

#%% open image file
# this part should be different based on the algorithm
# it calculate the radiance for next part
impath = r'E:\t0823x'
im = gdal.Open(impath+'/LC08_L1TP_128039_20190329_20190404_01_T1_B2.TIF',gdal.GA_ReadOnly)
geo = im.GetGeoTransform()
proj = im.GetProjection()
im = im.ReadAsArray()
im = im * 1.2903E-02 - 64.51279
im[np.where(im<0)] = 0

im7 = gdal.Open(impath+'/LC08_L1TP_128039_20190329_20190404_01_T1_B7.TIF',gdal.GA_ReadOnly)
im7 = im7.ReadAsArray()
im7 = im7*2.0000E-05-0.1

im3 = gdal.Open(impath+'/LC08_L1TP_128039_20190329_20190404_01_T1_B3.TIF',gdal.GA_ReadOnly)
im6 = gdal.Open(impath+'/LC08_L1TP_128039_20190329_20190404_01_T1_B6.TIF',gdal.GA_ReadOnly)

im4 = gdal.Open(impath+'/LC08_L1TP_128039_20190329_20190404_01_T1_B4.TIF',gdal.GA_ReadOnly)

im3 = im3.ReadAsArray()
im6 = im6.ReadAsArray()
im4 = im4.ReadAsArray()

im3 = im3*2.0000E-05-0.1
im6 = im6*2.0000E-05-0.1
im4 = im4*2.0000E-05-0.1

ndwi = (im3-im6)/(im3+im6)
ndvi = (im4-im7)/(im4+im7)
im[np.where(ndwi>0.1)] = 0
#im[np.where(ndvi<0.1)] = 0

del im3,im6,im4
im7 = im7/4 # surface reflectance estimated based on band relationship


#%% estimate surface reflectance based on 6S model and create a look-up table

# parameters for atmospheric correction
ab = []
if True:
    for aot in aots:
        a,b = iLUT(sz, wv, o3, aot, km)
        a,b = corr_ab(a,b,doy)
        ab.append([a,b,aot])

# the new look-up table
tb = np.zeros([Ls.shape[0],len(ab)+1])
count = 0
tb[:,0] = Ls
for each in ab:
    count += 1
    tb[:,count] = (Ls - each[0])/each[1]
    
# empty image to save AOD
aod = np.zeros([im.shape[0],im.shape[1]])

# check the best-matched AOD
time1 = time.time()
for i in range(im.shape[0]):
    if i%500==0:
        print('index:',i)
    for j in range(im.shape[1]):
        _l = im[i,j] # apparent reflectance
        if _l > 300 or _l < 0: # in case the radiance is too large or small
            continue
        else:
            sr_6s = tb[np.uint16(_l*10),1:] # surface reflectance estimated by 6S
            if sr_6s.max()<0: # impossible radiance
                continue
            sr =  np.abs(sr_6s - im7[i,j]) # check under which condition the surface reflectances match each other
            _aot = aots[np.argmin(sr)] # this line is quicker than the next line
#            _aot = np.argmin(sr)*gofaot
            aod[i,j] = _aot
print('look-up time:',time.time()-time1)

np.save('aod.npy',aod)
      
        
#%% fill the no data with random forest regressor
#aod = gdal.Open('aod8.tif').ReadAsArray()
regr = RandomForestRegressor(max_depth=2,random_state=0,n_estimators=100)

imx,imy = aod.shape

#%% sampling from data point
nosample = 40000
x,y = np.where(aod!=0)
idx = np.random.permutation(x.shape[0])[:nosample]
x = x[idx]
y = y[idx]
aod2 = aod[x,y]
xy = np.array([x,y]).T
regr.fit(xy, aod2)


#%% predict
x,y = np.where(aod==0)
xy = np.array([x,y]).T
aod3 = regr.predict(xy)
aod[x,y] = aod3

aod[np.where(im7==-0.1)] = 0 # this line masks out no data value, it depends on dataset

if True:
    if True:
        # save as geocode-tif
        name = 'aod'
        outdata = gdal.GetDriverByName('GTiff').Create(name+'.tif', imy, imx, 1, gdal.GDT_Float32)
        outdata.SetGeoTransform(geo)
        outdata.SetProjection(proj)
        outdata.GetRasterBand(1).WriteArray(aod)
        outdata.FlushCache() ##saves to disk!!
        outdata = None
    
    

    
    
