#!/usr/bin/python
# ---------------------------------------------------------------------------
# Copyright 2014, Houston Engineering Inc., All Rights Reserved
# Description: Non-Contributing Terrain Analysis - Prefill
# Author: Paul Hedlund
# Created: April 2014
# Updated: October 2017
# ---------------------------------------------------------------------------
import sys, datetime, arcpy, time, os
from arcpy.sa import *
from arcpy import env

def main():
	try:
		#Start tracking time ------------------------------------------------------------------------
		start = time.time()
		starttime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		#Check out Spatial Analyst Extensions -------------------------------------------------------
		blnLicSA = ExtensionManagment('spatial','Spatial Analyst')
		if blnLicSA:
			return

		#Script Settings----------------------------------------------------------------------------
		rawDEM = arcpy.GetParameterAsText(0)
		agreeDEM = arcpy.GetParameterAsText(1)
		fillDEM = arcpy.GetParameterAsText(2)
		fillDirectionRaster = arcpy.GetParameterAsText(3)
		maxFillDepth = arcpy.GetParameter(4)
		maxSurfaceArea = arcpy.GetParameter(5)
		outputPrefill = arcpy.GetParameterAsText(6)

		##Script Settings----------------------------------------------------------------------------
		#rawDEM = r'D:\ZMapdata\NonContrib\Depression_Evaluation\Input\raw_dem'
		#agreeDEM = r'D:\ZMapdata\NonContrib\Depression_Evaluation\Input\agree_dem'
		#fillDEM = r'D:\ZMapdata\NonContrib\Depression_Evaluation\Input\fillall'
		#fillDirectionRaster = r'D:\ZMapdata\NonContrib\Depression_Evaluation\Input\fdrfillall'
		#maxFillDepth = 0
		#maxSurfaceArea = 0
		#outputPrefill = r'D:\ZMapdata\NonContrib\1915250_non.gdb'

		# Set Geoprocessing environments ------------------------------------------------------------
		env.overwriteOutput = True
		tempGDB = arcpy.env.scratchGDB
		arcpy.env.scratchworkspace = tempGDB

		#Validate Raster Size among input rasters
		arcpy.AddMessage("Validate grid cell sizes ...")
		InputRasterList = []
		InputRasterList.append(rawDEM)
		InputRasterList.append(agreeDEM)
		InputRasterList.append(fillDEM)
		InputRasterList.append(fillDirectionRaster)
		blnValidate = ValidateGridSizeMatch(InputRasterList)
		if blnValidate:
			return

		#Constants  --------------------------------------------------------------------------------------------
		Input_raster_constant = "1"

		#Calculate Conversions
		minFillDepth = maxFillDepth / ( 12 * 3.28084 )
		minSurfaceArea = maxSurfaceArea * ( 43560 / (3.28084 ** 2))

		#-------------------------------------------------------------------------------------------------------
		arcpy.AddMessage('Set Null Process ...')
		valElapsed = time.time()
		null_deps = SetNull(Minus(fillDEM,agreeDEM), Input_raster_constant,'VALUE <= 0')
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Deps poly unfiltered ...')
		valElapsed = time.time()
		deps_poly_unfilt = tempGDB + os.sep + 'deps_poly_unfilt'
		arcpy.RasterToPolygon_conversion(null_deps, deps_poly_unfilt,'NO_SIMPLIFY', 'VALUE')
		arcpy.Delete_management(null_deps)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Deps quarter ac ...')
		valElapsed = time.time()
		Deps_quarter_ac = tempGDB + os.sep + 'Deps_quarter_ac'
		arcpy.Select_analysis(deps_poly_unfilt, Deps_quarter_ac, 'Shape_Area > 1000')
		arcpy.Delete_management(deps_poly_unfilt)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Deps quarter ...')
		valElapsed = time.time()
		Quart_ras = tempGDB + os.sep + 'Quart_ras'
		arcpy.PolygonToRaster_conversion(Deps_quarter_ac,'gridcode',Quart_ras,'CELL_CENTER','NONE','')
		arcpy.Delete_management(Deps_quarter_ac)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Region Group ...')
		valElapsed = time.time()
		region_ras = RegionGroup(Quart_ras,'EIGHT','WITHIN','ADD_LINK','')
		arcpy.Delete_management(Quart_ras)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Deps poly acre region ...')
		valElapsed = time.time()
		deps_poly_acre_region = tempGDB + os.sep + 'deps_poly_acre_region'
		arcpy.RasterToPolygon_conversion(region_ras,deps_poly_acre_region,'NO_SIMPLIFY','VALUE')
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Deps poly acre ...')
		valElapsed = time.time()
		deps_poly_acre = tempGDB + os.sep + 'deps_poly_acre'
		arcpy.Select_analysis(deps_poly_acre_region, deps_poly_acre, 'Shape_Area > ' + str(minSurfaceArea)) #minSurfaceArea
		arcpy.Delete_management(deps_poly_acre_region)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Polygon to raster ...')
		valElapsed = time.time()
		acre_ras = tempGDB + os.sep + 'acre_ras'
		arcpy.PolygonToRaster_conversion(deps_poly_acre, 'GRIDCODE',acre_ras,'CELL_CENTER','NONE','')
		arcpy.Delete_management(deps_poly_acre)
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Zonal stats ...')
		valElapsed = time.time()
		outSetNulldepthGrid = Minus(fillDEM,rawDEM) #hyd_less_raw
		outSetNulldepthGrid.save(tempGDB + os.sep + 'minustemp')
		max_depth = ZonalStatistics(acre_ras,'VALUE',outSetNulldepthGrid,'MAXIMUM','DATA')
		PrintTime(start,valElapsed,True)

		arcpy.AddMessage('Set Null Process ...')
		valElapsed = time.time()
		outSetNulldprworkspace = SetNull(max_depth,region_ras,'VALUE < ' + str(minFillDepth)) #minFillDepth #Filtered_Deps
		arcpy.Delete_management(region_ras)
		arcpy.Delete_management(acre_ras)
		PrintTime(start,valElapsed,True)

		#Add to Map
		AddRastertoMap(outputPrefill + r"\filtered_deps")
		AddRastertoMap(outputPrefill + r"\depth_grid")

		#Completed Time
		arcpy.AddMessage("Completion Time")
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		elapsedtime =  secondsToStr(time.time() - start)[:-4]
		arcpy.AddMessage("Start Time            : " + str(starttime))
		arcpy.AddMessage("End Time              : " + str(timestamp))
		arcpy.AddMessage("Processing Time       : " + str(elapsedtime))

		arcpy.AddMessage("Tool Prefill Complete!")

	except:
		strError = sys.exc_info()[1]
		intLineValue = sys.exc_info()[2]
		strLine = str(intLineValue.tb_lineno)
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		arcpy.AddMessage(timestamp + ': Error occured processing Prefill Depth and SA script! - ' + 'Line:' + strLine + ' - Error:' + str(strError))

#//////////////// Functions//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def secondsToStr(t):
	rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
	return "%d:%02d:%02d.%03d" % tuple(reduce(rediv,[[t*1000,], 1000,60,60]))

def ExtensionManagment(ExtID, ExtName):
	if arcpy.CheckExtension(ExtID) == "Available":
		arcpy.AddMessage("Checking out the " + ExtName + " extension ...")
		arcpy.CheckOutExtension(ExtID)
		return False
	elif arcpy.CheckExtension(ExtID) == "Unavailable":
		arcpy.AddError("The " + ExtName + " extension is currently unavailable")
		return True
	elif arcpy.CheckExtension(ExtID) == "NotLicensed":
		arcpy.AddError("You are currently not license to use " + ExtName + ", the tool can not be run!")
		return True
	elif arcpy.CheckExtension(ExtID) == "Failed":
		arcpy.AddError("A system failure occurred during the request!")
		return True

def PrintTime(start, valElapsed, blnShowElapsed):
	#Get total and elapsed time

	if not blnShowElapsed:
		arcpy.AddMessage(" - Total - " + secondsToStr(time.time() - start)[:-4])
	else:
		arcpy.AddMessage(" - Total - " + secondsToStr(time.time() - start)[:-4] + " (Elapsed: " + secondsToStr(time.time() - valElapsed)[:-4] + ")")

def ProductManagmentArcInfo(Product):
	#Check this is an ArcInfo License
	if arcpy.CheckProduct(Product) == "AlreadyInitialized":
		arcpy.AddMessage(Product + " license found...")
		return False
	elif arcpy.CheckProduct(Product) == "Available":
		arcpy.AddMessage(Product + " license found...")
		return False
	else:
		return True

def ProductManagment(Product):
	#Check this is an ArcInfo License
	if arcpy.CheckProduct(Product) == "AlreadyInitialized":
		arcpy.AddMessage(Product + " license found...")
		return False
	elif arcpy.CheckProduct(Product) == "Available":
		arcpy.AddMessage(Product + " license found...")
		return False
	elif arcpy.CheckProduct(Product) == "Unavailable":
		#arcpy.AddError("An " + Product + " license is required to run this tool!")
		return True
	elif arcpy.CheckProduct(Product) == "NotLicensed":
		#arcpy.AddError("An " + Product + " license is required to run this tool!")
		return True
	elif arcpy.CheckProduct(Product) == "Failed":
		arcpy.AddError("A system failure occurred during the request!")
		return True

def ValidateGridSizeMatch(InputRasterList):
	#Validate grid size
	blnResults = False
	i = 0
	for iRaster in InputRasterList:
		GetCellSize = arcpy.GetRasterProperties_management (iRaster, "CELLSIZEX")
		GridSize = float(GetCellSize.getOutput(0))
		if i <> 0:
			if not (GridSize - 0.02) <= preGridSize <= (GridSize + 0.02):
				blnResults = True
				break
		preGridSize = GridSize
		i += 1

	if blnResults:
		arcpy.AddError("The grid cell size does not match among all the input rasters!")
	return blnResults

def GetCellSize(InputRaster):
	#Get grid size
	GetCellSize = arcpy.GetRasterProperties_management (InputRaster , "CELLSIZEX")
	GridSize = GetCellSize.getOutput(0)
	arcpy.AddMessage("Raster Cellsize = " + GridSize)
	return float(GridSize)

def AddRastertoMap(InputRaster):
	try:
		mxd = arcpy.mapping.MapDocument("Current")
	except:
		return
	df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
	RasterFile = arcpy.mapping.Layer(InputRaster)
	RasterFile.visible = False
	arcpy.mapping.AddLayer(df, RasterFile, "TOP")

if __name__ == "__main__": main()