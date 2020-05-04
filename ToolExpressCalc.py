#!/usr/bin/python
# ---------------------------------------------------------------------------
# Copyright 2014, Houston Engineering Inc., All Rights Reserved
# Description: Non-Contributing Terrain Analysis - Prefill
# Author: Paul Hedlund
# Created: April 2014
# ---------------------------------------------------------------------------
import sys, datetime, arcpy, time
from arcpy.sa import *
from arcpy import env

def main():
	try:
		#Start tracking time ------------------------------------------------------------------------
		start = time.time()
		starttime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		#Check out Spatial Analyst Extensions -------------------------------------------------------
		blnLicSA = ExtensionManagment("spatial", "Spatial Analyst")
		if blnLicSA:
			return

		##Script Settings----------------------------------------------------------------------------
		#fillDirectionRaster = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb\fdr_total'
		#depressionPrefill = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb\Filtered_Depressions'
		#inputCNgrid = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb\curve_num'
		#inputRainfall = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb\rainfall2'
		#depthRaster = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb\raw_dem'
		#outputExcess = r'D:\ZMapdata\NonContrib\1915250_noncontribgdb.gdb'

		#Script Settings----------------------------------------------------------------------------
		fillDirectionRaster = arcpy.GetParameterAsText(0)
		depressionPrefill = arcpy.GetParameterAsText(1)
		inputCNgrid = arcpy.GetParameterAsText(2)
		inputRainfall = arcpy.GetParameterAsText(3)
		depthRaster = arcpy.GetParameterAsText(4)
		outputExcess = arcpy.GetParameterAsText(5)

		#Validate Raster Size among input rasters
		arcpy.AddMessage("Validate grid cell sizes ...")
		InputRasterList = []
		InputRasterList.append(fillDirectionRaster)
		InputRasterList.append(depressionPrefill)
		InputRasterList.append(inputCNgrid)
		InputRasterList.append(inputRainfall)
		InputRasterList.append(depthRaster)
		blnValidate = ValidateGridSizeMatch(InputRasterList)
		if blnValidate:
			return

		#Cell size
		rasterCellSurface = GetCellSize(fillDirectionRaster)

		# Set Geoprocessing environments
		tempGDB = arcpy.env.scratchGDB
		arcpy.env.scratchworkspace = tempGDB
		arcpy.env.overwriteOutput = True
		arcpy.env.snapRaster = fillDirectionRaster
		arcpy.env.cellSize = rasterCellSurface
		arcpy.env.extent = fillDirectionRaster

		numcores = multiprocessing.cpu_count() - 1
		if numcores > 4:
			arcpy.env.parallelProcessingFactor = '4'
		else:
			arcpy.env.parallelProcessingFactor = str(numcores)

		#--------------------------------------------------------------------------------------------

		# Process: Watershed (2)
		arcpy.AddMessage("Watershed (2) ...")
		valElapsed = time.time()
		outWatershed = Watershed(fillDirectionRaster,depressionPrefill, "VALUE")
		PrintTime(start,valElapsed,True)

		# Process: Lookup
		arcpy.AddMessage("Lookup ...")
		valElapsed = time.time()
		outLookup = Lookup(outWatershed,"COUNT")
		PrintTime(start,valElapsed,True)

		# Process: Zonal Statistics (14)
		arcpy.AddMessage("Calculate Mean CN ...")
		valElapsed = time.time()
		meanCN = ZonalStatistics(outWatershed, "VALUE", inputCNgrid, "MEAN", "DATA")
		PrintTime(start,valElapsed,True)

		# Process: Zonal Statistics (13)
		arcpy.AddMessage("Calcalulate Mean Rainfall ...")
		valElapsed = time.time()
		MeanRainfall = ZonalStatistics(outWatershed, "VALUE", inputRainfall, "MEAN", "DATA")
		PrintTime(start,valElapsed,True)

		# Process: Raster Calculator
		arcpy.AddMessage("Raster Calculator Math ...")
		valElapsed = time.time()
		SCS_pe = (Con((((1000 / meanCN) - 10) * 0.2) - MeanRainfall , (Square((MeanRainfall - (((1000 / meanCN) - 10) * 0.2)))) / (MeanRainfall + (0.8 * ((1000 / meanCN) - 10))) , 0 , "VALUE < 0" )) / (3.28084 * 12)
		PrintTime(start,valElapsed,True)

		del meanCN
		del MeanRainfall

		# Process: Build Raster Attribute Table
		arcpy.AddMessage("Build Raster Attribute Table ...")
		valElapsed = time.time()
		arcpy.BuildRasterAttributeTable_management(outWatershed, "Overwrite")
		PrintTime(start,valElapsed,True)

		# Process: Times
		arcpy.AddMessage("Times ...")
		valElapsed = time.time()
		outVolume = Times((rasterCellSurface **2), depthRaster)
		PrintTime(start,valElapsed,True)

		# Process: Minus (2)
		arcpy.AddMessage("Create depr_excess ...")
		valElapsed = time.time()
		minus1 = Minus(Times(Times(outLookup, (rasterCellSurface **2)), SCS_pe), ZonalStatistics(outWatershed, "VALUE", ExtractByMask(SetNull(outVolume, outVolume, "VALUE < 0"), depressionPrefill), "SUM", "DATA"))
		minus1.save(outputExcess + r"\depr_excess")
		PrintTime(start,valElapsed,True)

		del outWatershed
		del SCS_pe
		del outVolume
		del minus1

		# Process: Divide
		arcpy.AddMessage("Divide ...")
		valElapsed = time.time()
		outDivide = Divide(outputExcess + r"\depr_excess", outLookup)
		outDivide.save(outputExcess + r"\excess_percel")
		PrintTime(start,valElapsed,True)

		del outLookup
		del outDivide

		#Add to Map
		AddRastertoMap(outputExcess + r"\depr_excess")
		AddRastertoMap(outputExcess + r"\excess_percel")

		#Completed Time
		arcpy.AddMessage("Completetion Time")
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		elapsedtime =  secondsToStr(time.time() - start)[:-4]
		arcpy.AddMessage("Start Time            : " + str(starttime))
		arcpy.AddMessage("End Time              : " + str(timestamp))
		arcpy.AddMessage("Processing Time       : " + str(elapsedtime))

		arcpy.AddMessage("Tool Express Calc Complete!")

	except:
		strError = sys.exc_info()[1]
		intLineValue = sys.exc_info()[2]
		strLine = str(intLineValue.tb_lineno)
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		arcpy.AddMessage(timestamp + ': Error occured processing Express Calc script! - ' + 'Line:' + strLine + ' - Error:' + str(strError))

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

def GetCellSize(InputRaster):
	#Get grid size
	GetCellSize = arcpy.GetRasterProperties_management (InputRaster , "CELLSIZEX")
	GridSize = GetCellSize.getOutput(0)
	arcpy.AddMessage("Raster Cellsize = " + GridSize)
	return float(GridSize)

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