# -*- coding: utf-8 -*-
"""
Last updated on Aug 12 2019
@author: Shengjie Liu
@Email: liushengjie0756@gmail.com

Load a pretrained PMNet and a Zhuhai-1 hyperspectral image,
then estimate PM2.5 & PM10 concentration

"""
import numpy as np
import rscls
import matplotlib.pyplot as plt
import time
from keras import backend as K
import argparse
from keras.callbacks import EarlyStopping
import gdal
from keras.models import load_model

#%% arguments
# if script==True, arguments here will be ignored
m = 10
ang1 = 0.409838
ang2 = 50.135480/10
lat = 28.87/100
lng = 115.65/100

script = False # using script arguments

# base disk 
baseurl = 'G:/'

# hyperspectral image location
im_file = baseurl + r'orbita\data_32band\HAM1_20181006215942_0013_L1_MSS_CCD1.tif'

# load model created by demo_keras_predict.py
model_file = baseurl + r'orbita\data\model.h5'

## number of training samples per class
parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--im', type=str, default = None, help='Zhuhai-1 image file')
parser.add_argument('--model', type=str, default = None, help='pretrained model file')
parser.add_argument('--vbs', type=int, default = 0, help='verbose: 1=on, 0=off')
parser.add_argument('--m', type=int, default = 10)
parser.add_argument('--ang1', type=float, default = 0.4)
parser.add_argument('--ang2', type=float, default = 50.1)
parser.add_argument('--lat', type=float, default = 28.8)
parser.add_argument('--lng', type=float, default = 115.6)
args = parser.parse_args()

patch = 1
ensemble = 1  # if ensemble>1, snapshot ensemble activated 
vbs = 0

## network configuration
if script == True:
    vbs = args.vbs
    model_file = args.model
    im_file = args.im
    m = args.month
    ang1 = args.ang1
    ang2 = args.ang2/100
    lat = args.lat/100
    lng = args.lng/100


#%% predicted
if __name__ == '__main__':
    if True:
        time1 = int(time.time())
        K.clear_session()
            
        im = gdal.Open(im_file,gdal.GA_ReadOnly)
        projection = im.GetProjection()
        newgeo = im.GetGeoTransform()

        im = im.ReadAsArray()
        im = im.transpose(1,2,0)
        gt = np.ones([im.shape[0],im.shape[1]]).astype(int)
       
        im = np.float32(im)
        im = im/1000
        
        # 1006 nanchang
        months = np.ones([im.shape[0],im.shape[1],1])*m
        ang1 = np.ones([im.shape[0],im.shape[1],1])*ang1
        ang2 = np.ones([im.shape[0],im.shape[1],1])*ang2
        lat = np.ones([im.shape[0],im.shape[1],1])*lat
        lng = np.ones([im.shape[0],im.shape[1],1])*lng

        im = np.concatenate([im,months,ang1,ang2,lat,lng],axis=-1)
        
        cls1 = gt.max()

        im1x,im1y,im1z = im.shape
        
        
        # image controller
        c1 = rscls.rscls(im,gt,cls=cls1)
        c1.padding(patch)
        
        model = load_model(model_file)
        model.summary()
        
        
        time3 = int(time.time()) # start predicting
        
        # predict part
        # each time predict one row
        pre_all_1 = []
        pre_all_2 = []
        for i in range(ensemble):
            pre_rows_1 = []
            pre_rows_2 = []
            for j in range(im1x):
                if j%100==0:
                    print(j)
                #print(j) # uncomment to monitor predicing stages
                sam_row = c1.all_sample_row(j)
                sam_row = sam_row.reshape(sam_row.shape[0],im1z)
                pre_row1,pre_row2 = model.predict(sam_row)
                pre_row1 = pre_row1.reshape(1,im1y)
                pre_row2 = pre_row2.reshape(1,im1y)
                pre_rows_1.append(pre_row1)
                pre_rows_2.append(pre_row2)
            pre_all_1.append(np.array(pre_rows_1))
            pre_all_2.append(np.array(pre_rows_2))
            
        time4 = int(time.time())
        print('predict time:',time4-time3) # predict time

        # save PMx estimation in *.png
        pre_all_1 = np.array(pre_all_1).reshape(ensemble,im1x,im1y)
        pre1 = pre_all_1.reshape(im1x,im1y)
        rscls.save_cmap(pre1, 'jet', 'pre_pm25_'+str(time4)[-5:]+'.png')
        
        pre_all_2 = np.array(pre_all_2).reshape(ensemble,im1x,im1y)
        pre2 = pre_all_2.reshape(im1x,im1y)
        rscls.save_cmap(pre2, 'jet', 'pre_pm10_'+str(time4)[-5:]+'.png')
        
        # save as geotif, pm25
        name = 'pre_pm25_'+str(time4)[-5:]
        outdata = gdal.GetDriverByName('GTiff').Create(name+'.tif', im1y, im1x, 1, gdal.GDT_Float32)
        outdata.SetGeoTransform(newgeo)
        outdata.SetProjection(projection)
        outdata.GetRasterBand(1).WriteArray(pre1)
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        
        # save as geotif, pm10
        name = 'pre_pm10_'+str(time4)[-5:]
        outdata = gdal.GetDriverByName('GTiff').Create(name+'.tif', im1y, im1x, 1, gdal.GDT_Float32)
        outdata.SetGeoTransform(newgeo)
        outdata.SetProjection(projection)
        outdata.GetRasterBand(1).WriteArray(pre2)
        outdata.FlushCache() ##saves to disk!!
        outdata = None