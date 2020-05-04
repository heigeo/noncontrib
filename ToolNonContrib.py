#!/usr/bin/python
# ---------------------------------------------------------------------------
# Copyright 2014, Houston Engineering Inc., All Rights Reserved
# Description: Non-Contributing Terrain Analysis - Prefill
# Author: Paul Hedlund
# Created: April 2014
# ---------------------------------------------------------------------------
import sys, datetime, arcpy, time, os, multiprocessing
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
        rawDEM = arcpy.GetParameterAsText(0)
        agreeDEM = arcpy.GetParameterAsText(1)
        fillDEM = arcpy.GetParameterAsText(2)
        fillDirectionRaster = arcpy.GetParameterAsText(3)
        inputCNgrid = arcpy.GetParameterAsText(4)
        inputRainfall = arcpy.GetParameterAsText(5)
        maxFillDepth = arcpy.GetParameter(6)
        maxSurfaceArea = arcpy.GetParameter(7)
        blnMaxIter = arcpy.GetParameter(8)
        intMaxIter = arcpy.GetParameter(9)
        outputWorkspace = arcpy.GetParameterAsText(10)

        if not rawDEM: #If no parameter
            #Script Settings----------------------------------------------------------------------------
            rawDEM = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\WMD_3m_m'
            agreeDEM = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\AgreeDEM'
            fillDEM = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\hyd_dem'
            fillDirectionRaster = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\fdr_total'
            inputCNgrid = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\CN_Updated1'
            inputRainfall = r'D:\ZMapdata\NonContrib\New_NC_Areas\NC_Inputs.gdb\mw10yr24h_3mIn'
            maxFillDepth = 6
            maxSurfaceArea = 1
            blnMaxIter = False
            intMaxIter = 0
            outputWorkspace = r'D:\ZMapdata\NonContrib\New_NC_Areas\Thomas_NC_try\Test.gdb'

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

        #Cell size
        rasterCellSurface = GetCellSize(fillDirectionRaster)

        # Set Geoprocessing environments
        tempGDB = arcpy.env.scratchGDB
        arcpy.env.scratchworkspace = tempGDB
        arcpy.env.overwriteOutput = True
        arcpy.env.snapRaster = rawDEM
        arcpy.env.cellSize = rasterCellSurface
        arcpy.env.extent = rawDEM

        numcores = multiprocessing.cpu_count() - 1
        if numcores > 4:
            arcpy.env.parallelProcessingFactor = '4'
        else:
            arcpy.env.parallelProcessingFactor = str(numcores)

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

        #------ Tool Express Calc-------------------------------------------
        arcpy.AddMessage("Watershed (2) ...")
        valElapsed = time.time()
        outWatershedExpress = Watershed(fillDirectionRaster,outSetNulldprworkspace, "VALUE")
        PrintTime(start,valElapsed,True)

        arcpy.AddMessage("Lookup ...")
        valElapsed = time.time()
        outLookup = Lookup(outWatershedExpress,"COUNT")
        PrintTime(start,valElapsed,True)

        arcpy.AddMessage("Calculate Mean CN ...")
        valElapsed = time.time()
        meanCN = ZonalStatistics(outWatershedExpress, "VALUE", inputCNgrid, "MEAN", "DATA")
        PrintTime(start,valElapsed,True)

        arcpy.AddMessage("Calculate Mean Rainfall ...")
        valElapsed = time.time()
        MeanRainfall = ZonalStatistics(outWatershedExpress, "VALUE", inputRainfall, "MEAN", "DATA")
        PrintTime(start,valElapsed,True)

        arcpy.AddMessage("Raster Calculator Math ...")
        valElapsed = time.time()
        SCS_pe = (Con((((1000 / meanCN) - 10) * 0.2) - MeanRainfall , (Square((MeanRainfall - (((1000 / meanCN) - 10) * 0.2)))) / (MeanRainfall + (0.8 * ((1000 / meanCN) - 10))) , 0 , "VALUE < 0" )) / (3.28084 * 12)
        PrintTime(start,valElapsed,True)

        del meanCN
        del MeanRainfall

        arcpy.AddMessage("Build Raster Attribute Table ...")
        valElapsed = time.time()
        arcpy.BuildRasterAttributeTable_management(outWatershedExpress, "Overwrite")
        PrintTime(start,valElapsed,True)

        arcpy.AddMessage("Times ...")
        valElapsed = time.time()
        outVolume = Times((rasterCellSurface ** 2), outSetNulldepthGrid)
        PrintTime(start,valElapsed,True)

        del outSetNulldepthGrid

        arcpy.AddMessage("Create depr_excess ...")
        valElapsed = time.time()
        minusExcess2 = Minus(Times(Times(outLookup, (rasterCellSurface ** 2)), SCS_pe), ZonalStatistics(outWatershedExpress, "VALUE", ExtractByMask(SetNull(outVolume, outVolume, "VALUE < 0"), outSetNulldprworkspace), "SUM", "DATA"))
        PrintTime(start,valElapsed,True)

        del outWatershedExpress
        del SCS_pe
        del outVolume

        arcpy.AddMessage("Divide ...")
        valElapsed = time.time()
        outDivideExcessPercel = Divide(minusExcess2, outLookup)
        PrintTime(start,valElapsed,True)

        del outLookup

        # Tool Iteration--------------------------------------------------------------------------------------------
        maxExcess = 1.0
        intCount = 0
        excessLoop = minusExcess2
        outSetNull3 = None
        outWatershed3 = None
        deprPrefillLoop = outSetNulldprworkspace
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
            excessLoop = ZonalStatistics(outWatershed3, "VALUE", outDivideExcessPercel, "SUM", "DATA")

            maxExcessVar = arcpy.GetRasterProperties_management(excessLoop, "MAXIMUM", "")
            maxExcess = float(maxExcessVar.getOutput(0))
            arcpy.AddMessage(" ~ Max Excess = " + str(maxExcess))

            RasterCount = int(arcpy.GetCount_management(outWatershed3).getOutput(0))
            arcpy.AddMessage(" ~ Depression Count = " + str(RasterCount))

            PrintTime(start,valElapsed,True)

            if blnMaxIter:
                if intCount >= intMaxIter:
                    break

        # Process: Copy Raster
        arcpy.CopyRaster_management(outSetNull3,tempGDB + os.sep + 'final_deprtmp','','','','NONE','NONE','','NONE','NONE')
        arcpy.RasterToPolygon_conversion(tempGDB + os.sep + 'final_deprtmp',tempGDB + os.sep + 'deprpoly','NO_SIMPLIFY','VALUE')
        arcpy.Dissolve_management(tempGDB + os.sep + 'deprpoly', outputWorkspace + os.sep + 'final_depr',['gridcode'])

        arcpy.CopyRaster_management(outWatershed3,tempGDB + r'\final_depr_datmp','','','','NONE','NONE','','NONE','NONE')
        arcpy.RasterToPolygon_conversion(tempGDB + os.sep + 'final_depr_datmp',tempGDB + os.sep + 'deprdapoly' ,'NO_SIMPLIFY','VALUE')
        arcpy.Dissolve_management(tempGDB + os.sep + 'deprdapoly', outputWorkspace + os.sep + 'final_depr_da',['gridcode'])

        del outDivideExcessPercel
        del minusExcess2
        del outSetNulldprworkspace

        #Add to Map
        AddRastertoMap(outputWorkspace + r'\final_depr')
        AddRastertoMap(outputWorkspace + r'\final_depr_da')

        #Completed Time
        arcpy.AddMessage('Completion Time')
        timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        elapsedtime =  secondsToStr(time.time() - start)[:-4]
        arcpy.AddMessage("Start Time            : " + str(starttime))
        arcpy.AddMessage("End Time              : " + str(timestamp))
        arcpy.AddMessage("Processing Time       : " + str(elapsedtime))

        arcpy.AddMessage("Tool Full Non-Contributing Analysis Complete!")

    except:
        strError = sys.exc_info()[1]
        intLineValue = sys.exc_info()[2]
        strLine = str(intLineValue.tb_lineno)
        timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        arcpy.AddMessage(timestamp + ': Error occured processing Full Non-Contributing Analysis! - ' + 'Line:' + strLine + ' - Error:' + str(strError))

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
        return True
    elif arcpy.CheckProduct(Product) == "NotLicensed":
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