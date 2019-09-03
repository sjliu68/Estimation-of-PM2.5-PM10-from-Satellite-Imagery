# Name: ExtractMultiValuesToPoints_Ex_02.py
# Description: Extracts the cells of multiple rasters as attributes in
#    an output point feature class.  This example takes a multiband IMG
#    and two GRID files as input.
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *
import glob

# Set environment settings
env.workspace = r"I:\orbita\data"

# Set local variables
inPointFeatures = r"I:\orbita\data\sites\pm25_2018.shp"

tifs = glob.glob(r'I:\orbita\data\hsi\*.tif')

for tif in tifs:
    #print(tif)
    name = tif[27:32]+tif[41:43]
    print(name)

    inRasterList = [[tif,name]]
    arcpy.CheckOutExtension("Spatial")
    ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")

#inRasterList = [["C:/HAM2_20181001214539_0004_L1_MSS_CCD2.tif", "im"]]

# Check out the ArcGIS Spatial Analyst extension license
# arcpy.CheckOutExtension("Spatial")

# Execute ExtractValuesToPoints
# ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")
