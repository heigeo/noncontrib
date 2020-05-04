#!/usr/bin/python
# ---------------------------------------------------------------------------
# Copyright 2014, Houston Engineering Inc., All Rights Reserved
# Description: Non-Contributing Terrain Analysis - One Iteration
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

		#Script Settings----------------------------------------------------------------------------
		depressionPrefill = arcpy.GetParameterAsText(0)
		outputExcess = arcpy.GetParameterAsText(1)
		outputExcessPercel = arcpy.GetParameterAsText(2)
		fillDirectionRaster = arcpy.GetParameterAsText(3)
		blnMaxIter = arcpy.GetParameter(4)
		intMaxIter = arcpy.GetParameter(5)
		outputDeprWorkspace = arcpy.GetParameterAsText(6)

		# Set Geoprocessing environments ------------------------------------------------------------
		tempGDB = arcpy.env.scratchGDB
		arcpy.env.scratchworkspace = tempGDB
		arcpy.env.overwriteOutput = True
		arcpy.env.snapRaster = fillDirectionRaster
		#arcpy.env.cellSize = rasterCellSurface
		arcpy.env.extent = fillDirectionRaster

		numcores = multiprocessing.cpu_count() - 1
		if numcores > 4:
			arcpy.env.parallelProcessingFactor = '4'
		else:
			arcpy.env.parallelProcessingFactor = str(numcores)

		#Validate Raster Size among input rasters
		arcpy.AddMessage("Validate grid cell sizes ...")
		InputRasterList = []
		InputRasterList.append(depressionPrefill)
		InputRasterList.append(outputExcess)
		InputRasterList.append(outputExcessPercel)
		InputRasterList.append(fillDirectionRaster)
		blnValidate = ValidateGridSizeMatch(InputRasterList)
		if blnValidate:
			return

		# Tool Iteration--------------------------------------------------------------------------------------------
		maxExcess = 1.0
		intCount = 0
		excessLoop = outputExcess
		outSetNull3 = None
		outWatershed3 = None
		deprPrefillLoop = depressionPrefill
		while (maxExcess > 0):
			arcpy.AddMessage("---------------------------------------------------------------")
			intCount += 1
			arcpy.AddMessage("Iteration #" + str(intCount))

			del outSetNull3
			del outWatershed3

			# Process: Watershed
			arcpy.AddMessage("Process Watershed ...")
			valElapsed = time.time()
			outSetNull3 = SetNull(excessLoop, deprPrefillLoop, "VALUE >= 0")
			del deprPrefillLoop
			deprPrefillLoop = outSetNull3
			outWatershed3 = Watershed(fillDirectionRaster,outSetNull3, "VALUE")

			del excessLoop

			# Process: Zonal Statistics
			arcpy.BuildRasterAttributeTable_management(outWatershed3, "Overwrite")
			excessLoop = ZonalStatistics(outWatershed3, "VALUE", outputExcessPercel, "SUM", "DATA")

			# Process: Get Raster Properties
			maxExcessVar = arcpy.GetRasterProperties_management(excessLoop, "MAXIMUM", "")
			maxExcess = float(maxExcessVar.getOutput(0))
			arcpy.AddMessage(" ~ Max Excess = " + str(maxExcess))

			# Process: Get Raster Cell Count
			RasterCount = int(arcpy.GetCount_management(outWatershed3).getOutput(0))
			arcpy.AddMessage(" ~ Depression Count = " + str(RasterCount))

			PrintTime(start,valElapsed,True)

			if blnMaxIter:
				if intCount >= intMaxIter:
					break

		# Process: Copy Raster
		arcpy.CopyRaster_management(outSetNull3,tempGDB + os.sep + 'final_deprtmp','','','','NONE','NONE','','NONE','NONE')
		arcpy.RasterToPolygon_conversion(tempGDB + os.sep + 'final_deprtmp',tempGDB + os.sep + 'deprpoly','NO_SIMPLIFY','VALUE')
		arcpy.Dissolve_management(tempGDB + os.sep + 'deprpoly', outputDeprWorkspace + os.sep + 'final_depr',['gridcode'])

		arcpy.CopyRaster_management(outWatershed3,tempGDB + r'\final_depr_datmp','','','','NONE','NONE','','NONE','NONE')
		arcpy.RasterToPolygon_conversion(tempGDB + os.sep + 'final_depr_datmp',tempGDB + os.sep + 'deprdapoly' ,'NO_SIMPLIFY','VALUE')
		arcpy.Dissolve_management(tempGDB + os.sep + 'deprdapoly', outputDeprWorkspace + os.sep + 'final_depr_da',['gridcode'])

		#Add to Map
		AddRastertoMap(outputDeprWorkspace + r"\final_depr")
		AddRastertoMap(outputDeprWorkspace + r"\final_depr_da")

		#Completed Time
		arcpy.AddMessage("Completetion Time")
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		elapsedtime =  secondsToStr(time.time() - start)[:-4]
		arcpy.AddMessage("Start Time            : " + str(starttime))
		arcpy.AddMessage("End Time              : " + str(timestamp))
		arcpy.AddMessage("Processing Time       : " + str(elapsedtime))

		arcpy.AddMessage("Tool One Iteration Complete!")

	except:
		strError = sys.exc_info()[1]
		intLineValue = sys.exc_info()[2]
		strLine = str(intLineValue.tb_lineno)
		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

		arcpy.AddMessage(timestamp + ': Error occured processing One Iteration script! - ' + 'Line:' + strLine + ' - Error:' + str(strError))

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