#!/usr/bin/python
# ---------------------------------------------------------------------------
# Copyright 2015, Houston Engineering Inc., All Rights Reserved
# Description: Delineate Watersheds
# Author: Paul Hedlund
# Created: March 2015
# ---------------------------------------------------------------------------
import sys,os,datetime,arcpy,time
from arcpy.sa import *

def main():
	try:
		#Start tracking time ------------------------------------------------------------------------
		start = time.time()
		starttime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

		#Check out Spatial Analyst Extensions -------------------------------------------------------
		blnLicSA = ExtensionManagment('spatial','Spatial Analyst')
		if blnLicSA:
			return

		#Script Settings----------------------------------------------------------------------------
		fillDirectionRaster = arcpy.GetParameterAsText(0)
		catchment = arcpy.GetParameterAsText(1)
		catchmentfield = arcpy.GetParameterAsText(2)
		polylyr = arcpy.GetParameterAsText(3)
		polylyrfield = arcpy.GetParameterAsText(4)

		# Set Geoprocessing environments ------------------------------------------------------------
		tempGDB = arcpy.env.scratchGDB
		arcpy.env.scratchworkspace = tempGDB
		arcpy.env.overwriteOutput = True
		arcpy.env.snapRaster = fillDirectionRaster

		numcores = multiprocessing.cpu_count() - 1
		if numcores > 4:
			arcpy.env.parallelProcessingFactor = '4'
		else:
			arcpy.env.parallelProcessingFactor = str(numcores)

		#Adjoint looping ---------------------------------------------------------------------------------------------------------------
		arcpy.AddMessage('Begin looping through raster layer ...')
		fields = ['OID@',catchmentfield]
		cursorInsert = arcpy.da.InsertCursor(polylyr, ['SHAPE@',polylyrfield])
		with arcpy.da.SearchCursor(catchment,fields) as cursor:
			for row in cursor:
				valElapsed = time.time()
				arcpy.AddMessage(str(row[0]))
				con500000 = Con(catchment,catchment,'',catchmentfield + ' = ' + str(row[1]))
				con500000.save()
				arcpy.AddMessage(' - Watersheds ...')
				wshd500000 = Watershed(fillDirectionRaster,con500000,catchmentfield)
				arcpy.Delete_management(con500000)
				arcpy.AddMessage(' - Raster to poly ...')
				arcpy.RasterToPolygon_conversion(wshd500000,tempGDB + os.sep + 'wshdpoly','NO_SIMPLIFY',catchmentfield)
				arcpy.Delete_management(wshd500000)
				arcpy.AddMessage(' - Dissolves ...')
				arcpy.Dissolve_management(tempGDB + os.sep + 'wshdpoly',tempGDB + os.sep + 'wshddissolve',polylyrfield,'','MULTI_PART','DISSOLVE_LINES')
				arcpy.Delete_management(tempGDB + os.sep + 'wshdpoly')
				arcpy.AddMessage(' - Copy features ...')
				with arcpy.da.SearchCursor(tempGDB + os.sep + 'wshddissolve',['SHAPE@',polylyrfield]) as cursorDissolve:
					for rowDissolve in cursorDissolve:
						cursorInsert.insertRow((rowDissolve[0],rowDissolve[1]))
				arcpy.Delete_management(tempGDB + os.sep + 'wshddissolve')
				PrintTime(start,valElapsed,True)
		del cursorInsert

		#Completed Time
		arcpy.AddMessage('Completion Time')
		timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		elapsedtime =  secondsToStr(time.time() - start)[:-4]
		arcpy.AddMessage('Start Time            : ' + str(starttime))
		arcpy.AddMessage('End Time              : ' + str(timestamp))
		arcpy.AddMessage('Processing Time       : ' + str(elapsedtime))

		arcpy.AddMessage('Delineated Watersheds Complete!')
	except:
		strError = sys.exc_info()[1]
		intLineValue = sys.exc_info()[2]
		strLine = str(intLineValue.tb_lineno)
		timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

		arcpy.AddMessage(timestamp + ': Error occured processing Delineated Watersheds script! - ' + 'Line:' + strLine + ' - Error:' + str(strError))
#//////////////// Functions//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def secondsToStr(t):
	rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
	return '%d:%02d:%02d.%03d' % tuple(reduce(rediv,[[t*1000,], 1000,60,60]))

def ExtensionManagment(ExtID, ExtName):
	if arcpy.CheckExtension(ExtID) == 'Available':
		arcpy.AddMessage('Checking out the ' + ExtName + ' extension ...')
		arcpy.CheckOutExtension(ExtID)
		return False
	elif arcpy.CheckExtension(ExtID) == 'Unavailable':
		arcpy.AddError('The ' + ExtName + ' extension is currently unavailable')
		return True
	elif arcpy.CheckExtension(ExtID) == 'NotLicensed':
		arcpy.AddError('You are currently not license to use ' + ExtName + ', the tool can not be run!')
		return True
	elif arcpy.CheckExtension(ExtID) == 'Failed':
		arcpy.AddError('A system failure occurred during the request!')
		return True

def PrintTime(start, valElapsed, blnShowElapsed):
	#Get total and elapsed time

	if not blnShowElapsed:
		arcpy.AddMessage(' - Total - ' + secondsToStr(time.time() - start)[:-4])
	else:
		arcpy.AddMessage(' - Total - ' + secondsToStr(time.time() - start)[:-4] + ' (Elapsed: ' + secondsToStr(time.time() - valElapsed)[:-4] + ')')

if __name__ == "__main__": main()