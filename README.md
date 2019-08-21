# Estimation-of-PM2.5-PM10-from-satellite-imagery
Estimate PM2.5/PM10 from satellite imagery


## About
This repo is currently under construction.

## Notes

### formula of Sentinel-2 imagery
    theta = acos(cos(view_zenith_mean)*cos(sun_zenith)+sin(view_zenith_mean)*sin(sun_zenith)*cos(sun_azimuth - view_azimuth_mean))

    ndvi = (B11-B12)/(B11+B12)

    slope_ndvi = 
    if ndvi_swir<0.25 then 0.48 
    else if ndvi_swir>0.75 then 0.58
    else 0.48+0.2*(ndvi_swir-0.25)

    slope = slope_ndvi+0.002*theta-0.27

    yint = 0.00025*theta+0.033

    p66 = B12*slope+yint

    p66*0.49+0.005
