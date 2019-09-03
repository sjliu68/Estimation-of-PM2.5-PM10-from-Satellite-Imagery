# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 16:50:31 2019

@author: SJ
"""

import pandas as pd
from simpledbf import Dbf5
import numpy as np


dbf = Dbf5(r'I:\orbita\data\sites\pm10_all.dbf')
df = dbf.to_dataframe()

name = list(df.columns)
# 1-352: pm10 data
# 353,354: lat,lng
# 355 after: data of bands
# end: 662
# after 622: 2019
    
x = []
y = []
for clm in range(355,663,4):
    print(clm)
    print(name[clm])
#    clm = 355
    date = name[clm]
    date = 't'+'201'+date[3:8]
    try:
        data = df[date]
    except:
        continue
    a1 = np.array(df[name[clm]])
    a2 = np.array(df[name[clm+1]])
    a3 = np.array(df[name[clm+2]])
    a4 = np.array(df[name[clm+3]])
    b = np.where(a1!=-9999)
    c1 = a1[b]
    c2 = a2[b]
    c3 = a3[b]
    c4 = a4[b]
    c = np.concatenate([c1,c2,c3,c4],axis=0)
    try:
        c = c.reshape(-1,c4.shape[0]).T
    except:
        continue
    
    data = np.array(data)[b]
    d = np.where(data!=0)
    c = c[d]
    data = data[d].reshape(-1,1)
    month = np.array(date[5:7]).astype(int)
    month = np.ones([b[0].shape[0],1])*month
    month = month[d]
    ytmp = data
    xtmp = np.concatenate([c,month],axis=-1)
    lat = np.array(df[name[353]])[b][d].reshape(-1,1)
    lng = np.array(df[name[354]])[b][d].reshape(-1,1)
    xtmp = np.concatenate([xtmp,lat,lng],axis=-1)
    x.append(xtmp)
    y.append(ytmp)

#%%
x = np.concatenate(x)
y = np.concatenate(y)
y = y.reshape(-1)

#%%
ndvi = (x[:,2]-x[:,1])/(x[:,2]+x[:,1])
ndvi = ndvi.reshape(-1,1)
subx = x[:,3]-x[:,0]
subx = subx.reshape(-1,1)
x = np.concatenate([x,ndvi,subx],axis=-1)
#%%
np.random.seed(1337)
nos = 90
idx = np.random.permutation(x.shape[0])
x_train = x[idx][:nos]
y_train = y[idx][:nos]

x_test = x[idx][nos:]
y_test = y[idx][nos:]

from sklearn.ensemble import RandomForestRegressor as RF
model = RF(max_depth=2,random_state=1337,n_estimators=10)
model.fit(x_train,y_train)
print(model.score(x_test,y_test))
#print(model.feature_importances_)
y_pre = model.predict(x_test)
