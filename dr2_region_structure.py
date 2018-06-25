import sys
import os

#config

rootDir = 'd:/projects/astronomy/gaia_dr2/'

#code

def processIso(structures,o,s,prevIso,prevStructureCount,startList,startIso,labelPrefix):
    iso = o['iso']
    region = o['region']
    starCount = o['count']
    occurrence = o['occurrence']
    if prevIso == 0:
        for o2 in sorted(startList, key=lambda x: x['count'], reverse=True):
            s = processIso(structures,o2,s,iso,0,startList,startIso,labelPrefix)
    else:
        if (iso in structures) and (region in structures[iso]):
            structureCount = len(structures[iso][region])
        else:
            structureCount = 0

        tr = labelPrefix+' '+str(iso)+'-'+region+ " ("+str(occurrence)+" of "+str(starCount)+"): "+str(structureCount)
        #tabCount = (iso-startIso)//5
        tabCount = iso-startIso

        if occurrence > 0.5*starCount:
            if starCount >= countLimit:
                if (prevStructureCount == 1) and (prevIso < iso):
                    s += ' '+tr
                else:
                    s += "\n"+(tabCount*"\t")+tr        
            
            if (iso in structures) and (region in structures[iso]):
                for o2 in sorted(structures[iso][region], key=lambda x: x['count'], reverse=True):
                    s = processIso(structures,o2,s,iso,structureCount,startList,startIso,labelPrefix)
    return s


isoList = range(5,100,1)
isoType = 'hot'
labelPrefix = 'TR1'
countLimit = 5

structureDir = rootDir+'output/slices/'+isoType+'/structure/'
if not os.path.isdir(structureDir):
    os.mkdir(structureDir)

gp = open(structureDir+'structure_tab_iso_5.csv','w')

startStructure = {'iso':isoList[0],'region':'','count':0,'occurrence':0}

stars = {}

print("getting regions")

startIso = isoList[0]
startList = []
isoFile = rootDir+'output/slices/'+isoType+'/csv2/regions_'+str(startIso)+'.csv'
fp = open(isoFile,'r')
line = fp.readline()
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        region,polycount,regionLength,x,y,z,xmin,xmax,ymin,ymax,zmin,zmax,count = bits
        if int(count) >= countLimit:
            startList.append({'iso':startIso,'region':region,'count':int(count),'occurrence':int(count)})
    line = fp.readline()
fp.close()

print("getting stars")
for iso in isoList:
    if iso not in stars:
        stars[iso] = {}
    regionsFile = rootDir+'output/slices/'+isoType+'/csv2/stars_in_regions_'+str(iso)+'.csv'
    fp = open(regionsFile,'r')
    line = fp.readline()
    while len(line) != 0:
        bits = line.strip().split(',')
        if len(bits) > 1:
            name, colourIndex, xg, yg, zg, glon, glat, m, plx,plx_over_err,extinction,excess,nonNullCut,flagCut,dataCut, region = bits
            if region not in stars[iso]:
                stars[iso][region] = []
            stars[iso][region].append(name)
        line = fp.readline()
fp.close()

print("building structures")
structures = {}

for i in range(0,len(isoList)-1):
    iso1 = isoList[i]
    print(iso1)
    iso2 = isoList[i+1]
    for region2 in stars[iso2]:
        starCount = len(stars[iso2][region2])        
        for region1 in stars[iso1]:
            occurrence = 0
            for i in range(0,len(stars[iso2][region2])):
                starName = stars[iso2][region2][i]
                if starName in stars[iso1][region1]:
                    occurrence += 1
            if occurrence >= countLimit:
                tr1 = labelPrefix+' '+str(iso1)+'-'+region1
                tr2 = labelPrefix+' '+str(iso2)+'-'+region2
                #print(tr2+' is inside '+tr1)
                if iso1 not in structures:
                    structures[iso1] = {}
                if region1 not in structures[iso1]:
                    structures[iso1][region1] = []
                structures[iso1][region1].append({'iso':iso2,'region':region2,'count':starCount,'occurrence':occurrence})
                gp.write((','.join([str(iso2),region2,str(starCount),str(occurrence),str(iso1),region1]))+"\n")

gp.close()

#print(structures[5])

# gp = open('d:/projects/astronomy/gaia/temp_sigma_15/csv/structure3.csv','w')

# gp.write(processIso(structures,{'iso':5,'region':'5','count':18778},''))

# gp.close()


gp = open(structureDir+'structure_tab_iso_5.txt','w')
gp.write(processIso(structures,startStructure,'',0,1,startList,startIso,labelPrefix)[1:])
gp.close()