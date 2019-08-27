# Name: ExtractMultiValuesToPoints_Ex_02.py
# Description: Extracts the cells of multiple rasters as attributes in
#    an output point feature class.  This example takes a multiband IMG
#    and two GRID files as input.
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

# Set environment settings
env.workspace = "C:/sapyexamples/data"

# Set local variables
inPointFeatures = "F:/t0826/pm25_2018.shp"
inRasterList = [["C:/HAM2_20181001214539_0004_L1_MSS_CCD2.tif", "im"]]

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute ExtractValuesToPoints
ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")
