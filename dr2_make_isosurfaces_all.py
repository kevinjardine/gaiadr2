import vtk
import time
import sys
import os
import copy
import math
import psutil
from time import gmtime, strftime

#config

rootDir = 'd:/projects/astronomy/gaia_dr2/'

#code

binSize = 3

w = 3000
z_height = 600//binSize
doRegions = True
doReducePolys = True
reducePolysLimit = 32000
poeLimit = 10
ciLimit = 0 #OB
magLimit = 7

polyLimit = 5000

percentages = range(99,4,-1)

sliceDir = rootDir+'output/slices/hot/16bit/'
csvDir = rootDir+'output/slices/hot/csv2/'
isoDir = rootDir+'output/slices/hot/iso2/'

numberLimit = 0

if not os.path.isdir(csvDir):
    os.mkdir(csvDir)

if not os.path.isdir(isoDir):
    os.mkdir(isoDir)

stars = {}
fp = open(rootDir+'output/star_list/all_stars_0.1.csv','r')
line = fp.readline()

while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        name, colourIndex, xg, yg, zg, glon, glat, m, plx,plx_over_err,extinction,excess,nonNullCut,flagCut,dataCut = bits
        poe = float(plx_over_err)
        absMag = float(m)
        ci = float(colourIndex)
        if (poe > poeLimit) and (flagCut == '1') and (dataCut == '1') and (absMag < magLimit):
            stars[name] = {'line':line.strip(),'ci':colourIndex,'center':[float(xg),float(yg),float(zg)]}
    line = fp.readline()
fp.close()

print('stars',len(stars))

# for some reason the isosurfaces are generated slightly off centre

sunPosition = [1009,999,200]

for percent in percentages:
    print('percent: '+str(percent)+'%',strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    starRegion = {}

    isoValue = int(65536*percent/100 + 0.5)
    # print("about to open volume read")

    reader = vtk.vtkVolume16Reader()
    
    reader.SetFilePattern('%sslice_%04d.pgm')

    # print("setting image range")
    
    reader.SetImageRange(0,z_height*2-1)

    # print("setting data spacing")
    reader.SetDataSpacing(1,1,1)
    # print("setting data dimensions")
    reader.SetDataDimensions (2*w//binSize,2*w//binSize)

    # print("update")
    reader.SetFilePrefix(sliceDir)
    
    # print("running vtkSliceCubes")
    sc = vtk.vtkSliceCubes()
    sc.SetReader(reader)
    
    sc.SetFileName(isoDir+'iso.tri')
    sc.SetLimitsFileName(isoDir+'iso.lim')
    sc.SetValue(isoValue)
    
    sc.Update()

    # read from file
    # print("creating cube reader")
    mcReader = vtk.vtkMCubesReader()
    mcReader.SetFileName(isoDir+'iso.tri')
    # print("creating limits file")
    mcReader.SetLimitsFileName(isoDir+'iso.lim')
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(mcReader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(w,w)
    renWin.AddRenderer(ren)
    ren.AddActor(actor)

    # print("creating obj exporter")
    writer = vtk.vtkOBJExporter()
    writer.SetFilePrefix(isoDir+'iso_'+str(percent)+'_percent')
    writer.SetInput(renWin)
    writer.Write()

    # print("creating append filter")
    
    polyDataAccum = vtk.vtkPolyData()

    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputConnection(mcReader.GetOutputPort())
    connectivity.SetExtractionModeToSpecifiedRegions()
    connectivity.ScalarConnectivityOff()
    connectivity.Update()

    numberOfRegions = connectivity.GetNumberOfExtractedRegions()
    regionSizes = connectivity.GetRegionSizes()
    try:
        print(percent,'number of regions',numberOfRegions)
    except:
        print("weird print error")

    if doRegions:

        percentageDir = isoDir+'iso_'+str(percent)+'_percent/'
        if not os.path.isdir(percentageDir):
            os.mkdir(percentageDir)
        else:
            for f in os.listdir(percentageDir):
                os.remove(percentageDir+f) 

        setEncPts = vtk.vtkSelectEnclosedPoints()
        setEncPts.SetTolerance(.000001) 

        fp = open(csvDir+'regions_'+str(percent)+'.csv','w')

        totalCount = 0
        for i in range(0,numberOfRegions):
            #print(i,strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            polys2 = regionSizes.GetTuple(i)
            if polys2[0] > polyLimit:
                count = 0
                connectivity.InitializeSpecifiedRegionList() 
                connectivity.AddSpecifiedRegion(i)
                connectivity.Update()

                polyData = connectivity.GetOutput()        

                regionLength = polyData.GetLength()
                polys = 0           
                
                if regionLength > 0:
                    c = polyData.GetCenter()
                    polys = polyData.GetNumberOfPolys()
                    
                    (xmin,xmax,ymin,ymax,zmin,zmax) = polyData.GetBounds()  
                    setEncPts.Initialize(polyData)
                    for starName in stars:
                        p = stars[starName]['center']
                        if setEncPts.IsInsideSurface((sunPosition[0]+p[1]/binSize),(sunPosition[1]-p[0]/binSize),(sunPosition[2]+p[2]/binSize)) != 0:
                            starRegion[starName] = i
                            count += 1
                    setEncPts.Complete()
                s = ','.join(map(str,[i,polys,regionLength,c[0],c[1],c[2],xmin,xmax,ymin,ymax,zmin,zmax,count]))
                fp.write(s+"\n")
                totalCount += count
                if count >= numberLimit:
                    if doReducePolys:
                        deci = vtk.vtkDecimatePro()
                        deci.SetInputData(polyData)
                        if polys > reducePolysLimit:
                            print('decimating from',polys)
                            reduction = reducePolysLimit/polys
                            # do not try more than a 90% reduction
                            if reduction < 0.1:
                                reduction = 0.1
                            print("target reduction",reduction)
                        else:
                            reduction = 0.99
                            
                        deci.SetTargetReduction(1-reduction)
                        #deci.PreserveTopologyOn()
                        deci.Update()
                        polyData = deci.GetOutput()
                        
                        if polys > reducePolysLimit:
                            polysCount = polyData.GetNumberOfPolys()
                            print("new polys",polysCount)

                    mapper = vtk.vtkPolyDataMapper()
                    mapper.SetInputData(polyData)
                    mapper.Update()

                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    ren = vtk.vtkRenderer()
                    renWin = vtk.vtkRenderWindow()
                    renWin.SetSize(800,800)
                    renWin.AddRenderer(ren)
                    ren.AddActor(actor)

                    writer = vtk.vtkOBJExporter()
                    writer.SetFilePrefix(percentageDir+'region_'+str(i))
                    writer.SetInput(renWin)
                    writer.Write()

                    appendFilter = vtk.vtkAppendPolyData()
                    appendFilter.AddInputData(polyData)
                    appendFilter.AddInputData(polyDataAccum)
                    appendFilter.Update()

                    cleanFilter = vtk.vtkCleanPolyData()
                    cleanFilter.SetInputData(appendFilter.GetOutput())
                    cleanFilter.Update()

                    polyDataAccum = cleanFilter.GetOutput()
                   
                    try:
                        print(s)
                    except:
                        print('weird print error')
                    #print(psutil.virtual_memory())          
            
        fp.close()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polyDataAccum)
        mapper.Update()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        renWin.SetSize(w,w)
        renWin.AddRenderer(ren)
        ren.AddActor(actor)

        writer = vtk.vtkOBJExporter()
        writer.SetFilePrefix(isoDir+'iso_'+str(percent)+'_percent_filtered')
        writer.SetInput(renWin)
        writer.Write()
        
        fp = open(csvDir+'stars_in_regions_'+str(percent)+'.csv','w')
        for starName in stars:
            if starName in starRegion:
                fp.write(stars[starName]['line']+','+str(starRegion[starName])+"\n")
        fp.close()
