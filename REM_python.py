# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# REM_python.py
# Created on: 2015-07-14 09:39:18.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: REM_python <Input_Ground_DEM> <REM_Output> <Z_value_field> <Output_cell_size> <REM_w_Negatives> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
import arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Script arguments
## Input_Ground_DEM = arcpy.GetParameterAsText(0)
Input_Ground_DEM = "C:\\Users\\dknapp\\Desktop\\Ecuador_temp\\ecuador_srtm_30m_v3_envi_filled_trimmed.dat"

## REM_Output = arcpy.GetParameterAsText(1)
## if REM_Output == '#' or not REM_Output:
REM_Output = "C:\\Users\\dknapp\\Desktop\\Ecuador_temp\\ecuador_REM.dat" # provide a default value if unspecified

## Z_value_field = arcpy.GetParameterAsText(2)
## if Z_value_field == '#' or not Z_value_field:
Z_value_field = "GRID_CODE" # provide a default value if unspecified

## Output_cell_size = arcpy.GetParameterAsText(3)
## if Output_cell_size == '#' or not Output_cell_size:
Output_cell_size = "30" # provide a default value if unspecified

## REM_w_Negatives = arcpy.GetParameterAsText(4)
## if REM_w_Negatives == '#' or not REM_w_Negatives:
REM_w_Negatives = "C:\\Users\\dknapp\\Desktop\\Ecuador_temp\\ecuador_with_negatives" # provide a default value if unspecified

# Local variables:
Stream_Elevation_Raster = Input_Ground_DEM
Stream_Elev_Pts = Stream_Elevation_Raster
Elev_of_Nearest_Stream_Raster = Stream_Elev_Pts
SingleOutput3 = Input_Ground_DEM
Fill_SingleO1 = SingleOutput3
FlowDir_fill2 = Fill_SingleO1
FlowAcc_Flow2 = FlowDir_fill2
strmRaster = FlowAcc_Flow2
Output_drop_raster = Fill_SingleO1

print("STARTING PROCESS")

# Process: Convert -9999 to NoData
tempFile = SetNull(Input_Ground_DEM == -32768,Input_Ground_DEM)
## arcpy.gp.SingleOutputMapAlgebra_sa("setnull(Input_Ground_DEM == -32768,Input_Ground_DEM)", SingleOutput3, "''")
arcpy.gp.SingleOutputMapAlgebra_sa(tempFile, SingleOutput3, "''")
print("FINSHED CONVERTING -9999 to NoData")

# Process: Fill
arcpy.gp.Fill_sa(SingleOutput3, Fill_SingleO1, "")
print("FINSHED FILL PROCESS")

# Process: Flow Direction
arcpy.gp.FlowDirection_sa(Fill_SingleO1, FlowDir_fill2, "NORMAL", Output_drop_raster)
print("FINSHED FLOW DIRECTION")

# Process: Flow Accumulation
arcpy.gp.FlowAccumulation_sa(FlowDir_fill2, FlowAcc_Flow2, "", "FLOAT")
print("FINSHED FLOW ACCUMULATION")

# Process: Stream Definition
arcpy.gp.SingleOutputMapAlgebra_sa("setnull(FlowAcc_Flow2 < 11250, 1)", strmRaster, "C:\\Users\\dknapp\\Documents\\ArcGIS\\Default.gdb\\FlowAcc_Flow2")
print("FINSHED STREAM DEFINITION")

# Process: Create Strm Elv Raster
arcpy.gp.SingleOutputMapAlgebra_sa("strmRaster * Input Ground DEM", Stream_Elevation_Raster, "C:\\Users\\dknapp\\Documents\\ArcGIS\\Default.gdb\\SingleOutput5;''")
print("FINSHED STREAM ELEVATION RASTER")

# Process: Raster to Point
arcpy.RasterToPoint_conversion(Stream_Elevation_Raster, Stream_Elev_Pts, "VALUE")
print("FINSHED RASTER TO POINT")

# Process: Natural Neighbor
arcpy.gp.NaturalNeighbor_sa(Stream_Elev_Pts, Z_value_field, Elev_of_Nearest_Stream_Raster, Output_cell_size)
print("FINSHED NATURAL NEIGHBOR")

# Process: Subtract Strm Elv from DEM
arcpy.gp.SingleOutputMapAlgebra_sa("Input Ground DEM - Elev of Nearest Stream Raster", REM_w_Negatives, "'';C:\\Users\\dknapp\\Documents\\ArcGIS\\Default.gdb\\Natural_Rast2")
print("FINSHED SUBTRACT STREAM ELEV FROM DEM")

# Process: Zero Out Negatives
arcpy.gp.SingleOutputMapAlgebra_sa("con(REM w Negatives < 0,0,REM w Negatives)", REM_Output, "C:\\Users\\dknapp\\Documents\\ArcGIS\\Default.gdb\\SingleOutput7")
print("FINSHED ZERO OUT NEGATIVES")
print("FINSHED ALL!")
