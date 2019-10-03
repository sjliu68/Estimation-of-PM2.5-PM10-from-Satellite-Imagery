# Overview
This repo introduces two methods to estimate the air quality from satellite imagery.
- estimation of AOD values based on 6S radiative transfer model, or
- directly PM2.5/PM2.10 estimation from TOA reflectance

There are currently two case study, one based on Landsat-8 satellite data and the other based on Zhuhai-1 hyperspectral data.

**Note: This repo is currently under construction.**

## Based on 6S model to estimate AOD

- First, one needs to create a lookup table (LUT) from the 6S model. This Python version of 6S emulator is strongly recommended: https://github.com/samsammurphy/6S_emulator
- After creating the lookup table, run **estimate_aod.py** based on your Landsat-8 data



## Directly PM2.5/PM10 estimation from TOA reflectance using Zhuhai-1 hyperspectral data

**To convert Zhuhai-1 hyperspectral data to TOA reflectance, please refer to:**
https://github.com/stop68/Orbita-Hyperspectral-Imagery-to-Top-of-Atmosphere-Reflectance

For this method, we need the following data to build the model
- ground truth or site-based PM2.5/PM10 data (as label)
- a large amount of satellite imagery representing TOA reflectance (as variables)

After collection of the data, 
- run *extract_values.py* to create a excel table, containing the value of PM2.5 of each record and its corresponding satellite image
- run *train.py* to train a model, either random or DN
- the *train.py* also leaves out data for validation
- run *predict.py* to estimate PM2.5 based on the input image


