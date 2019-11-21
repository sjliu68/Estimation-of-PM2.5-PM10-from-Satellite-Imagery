# Overview
This repo introduces two methods to estimate the air quality from satellite imagery.
- estimation of AOD values based on 6S radiative transfer model, or
- directly PM2.5/PM2.10 estimation from TOA reflectance

There are currently two case study, one based on Landsat-8 satellite data and the other based on Zhuhai-1 hyperspectral data.


## Directly estimate PM2.5/PM10 from TOA reflectance using Zhuhai-1 data

### Using the pretrained model to estimate PMx concentration


To use the pretrained model in *demo_predict.py*, you may change the arguments directly in the script or use the inference below (plz change inference to True before usage):

```bash
python demo_predict.py --im 'G:/orbita/data_32band/HAM1_20181006215942_0013_L1_MSS_CCD1.tif' --model model_pmnet_v0.1.h5 --m 10 --ang1 0.4 --ang2 50.1 --lat 28.8 --lng 115.6
```

Here are the parameters availble for inference, you may find them in the header pdf of Zhuhai-1 raw data

```
--im        Zhuhai-1 hyperspectral image location
--model     pretrained model location
--m         month
--ang1      off-nadir angle, 侧摆角
--ang2      solar zenith angle, 太阳高度角
--lat       centered latitude of the hyperspectral image
--lng       centered longitude of the hyperspectral image
```

The input image is Zhuhai-1 TOA reflectance hyperspectral image in 32 bands.

**To convert the raw Zhuhai-1 hyperspectral data to TOA reflectance, please refer to:**

https://github.com/stop68/Orbita-Hyperspectral-Imagery-to-Top-of-Atmosphere-Reflectance

### Training

For this method, we need the following data to build the model
- ground truth or site-based PM2.5/PM10 data (as label)
- a large amount of satellite imagery representing TOA reflectance (as variables)

After collection of the data, 
- [x] run *extract_values.py* to create a excel table, containing the value of PM2.5 of each record and its corresponding satellite image *completed*
- [ ] *train.py* to train a model *todo*
- [x] *demo_predict.py* to estimate PM2.5 based on the input image based on the pretrained model *completed*


## Based on 6S model to estimate AOD

*Note: this part is in experiment*

- First, one needs to create a lookup table (LUT) from the 6S model. This Python version of 6S emulator is strongly recommended: https://github.com/samsammurphy/6S_emulator
- After creating the lookup table, run **estimate_aod.py** based on your Landsat-8 data



