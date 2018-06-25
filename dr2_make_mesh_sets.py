import vtk
import math
import sys
import os

def prune(r,d,a,b):
    d1,r1 = r.split('-')
    if d1 == d:
        b.append(r)
    elif r in a:
        for r2 in a[r]:
            b = prune(r2,d,a,b)
    return b

def getLeaves(r,m,c,a):
    leaves = []
    if r in a:
        for b in a[r]:
            if c[b] > m:
                leaves2 = getLeaves(b,m,c,a)
                if len(leaves2) > 0:
                    leaves += leaves2
                else:
                    leaves += [b]
            else:
                # does this actually work?
                leaves += [b]
    return leaves
    

rootDir = 'd:/projects/astronomy/gaia_dr2/'

leaves = {}
sub_regions = {}
regions = set()
region_data = []
start_region = 78
maximum_stars = 2000
region_counts = {}
#star_count_min = 25
# star_count_min = 30
#star_count_min = 50
star_count_min = 50
star_count_max = 10000000
#star_count_min = 5
leaf_star_count_min = 50
star_count_prune = 20
labels = {}
centres = {}
counts = {}
sunPosition = [1008.97,998.96,199.96]

very_ionizing_star_regions = set()
very_ionizing_peaks = set()

some_ionizing_star_regions = set()
some_ionizing_peaks = set()

large_non_ionizing_star_regions = set()
large_non_ionizing_peaks = set()

medium_non_ionizing_star_regions = set()
medium_non_ionizing_peaks = set()

fp = open(rootDir+'output/release/ranges.csv','r')

regions = set()
region_count = {}

line = fp.readline()

while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        region,count = bits
        regions.add(region)
    line = fp.readline()
fp.close()

print('regions',len(regions))

fileName = rootDir+'output/release/dr2_ionizing_stars_per_range.csv'
fp = open(fileName,'r')
line = fp.readline()

while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        region,count = bits
        if region in regions:
            count = int(count)
            #region_count[region] = int(count)
            if count >= 10:
                very_ionizing_star_regions.add(region)
            elif count >= 5:
                some_ionizing_star_regions.add(region)
    line = fp.readline()
fp.close()

print('very ionizing regions',len(very_ionizing_star_regions))
print('some ionizing regions',len(some_ionizing_star_regions))

fn = rootDir+'output/slices/hot/structure/structure_tab_iso_5_full.csv'
fp = open(fn,'r')
line = fp.readline()
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        iso,region,cx,cy,cz,starCount,iso1,region1 = bits
        slug = iso+'-'+region
        centres[slug] = [cx,cy,cz]
        counts[slug] = int(starCount)
        if iso1 != '':
            slug1 = iso1+'-'+region1
            if slug1 not in sub_regions:
                sub_regions[slug1] = []
            sub_regions[slug1].append(slug)
    line = fp.readline()
fp.close()

star_count_min = 50
star_count_max = 10000000

for identified_region in regions:
    #if identified_region in some_ionizing_star_regions:
    if (identified_region not in very_ionizing_star_regions) and (identified_region not in some_ionizing_star_regions):
        star_count = counts[identified_region]
        if ( star_count >= star_count_min) and (star_count <= star_count_max):
            large_non_ionizing_star_regions.add(identified_region)

star_count_min = 25
star_count_max = 49

for identified_region in regions:
    #if identified_region in some_ionizing_star_regions:
    if (identified_region not in very_ionizing_star_regions) and (identified_region not in some_ionizing_star_regions):
        star_count = counts[identified_region]
        if ( star_count >= star_count_min) and (star_count <= star_count_max):
            medium_non_ionizing_star_regions.add(identified_region)

print('large non ionizing regions',len(large_non_ionizing_star_regions))
print('medium non ionizing regions',len(medium_non_ionizing_star_regions))

for region in very_ionizing_star_regions:
    for leaf in getLeaves(region,leaf_star_count_min,counts,sub_regions):
        very_ionizing_peaks.add(leaf)

for region in some_ionizing_star_regions:
    for leaf in getLeaves(region,leaf_star_count_min,counts,sub_regions):
        if leaf not in very_ionizing_peaks:
            some_ionizing_peaks.add(leaf)
        else:
            print('very or some ionizing dup peak',leaf)

for region in large_non_ionizing_star_regions:
    for leaf in getLeaves(region,leaf_star_count_min,counts,sub_regions):
        if leaf not in (very_ionizing_peaks|some_ionizing_peaks):
            large_non_ionizing_peaks.add(leaf)
        else:
            print('very, some or large ionizing dup peak',leaf)

for region in medium_non_ionizing_star_regions:
    for leaf in getLeaves(region,leaf_star_count_min,counts,sub_regions):
        if leaf not in (very_ionizing_peaks|some_ionizing_peaks|large_non_ionizing_peaks):
            medium_non_ionizing_peaks.add(leaf)
        else:
            print('very, some, large or medium ionizing dup peak',leaf)


meshes = [
    [very_ionizing_star_regions,'very_ionizing_ranges'],
    [very_ionizing_peaks,'very_ionizing_peaks'],
    [some_ionizing_star_regions,'some_ionizing_ranges'],
    [some_ionizing_peaks,'some_ionizing_peaks'],
    [large_non_ionizing_star_regions,'non_ionizing_ge_50_stars_ranges'],
    [large_non_ionizing_peaks,'non_ionizing_ge_50_stars_peaks'],
    [medium_non_ionizing_star_regions,'non_ionizing_ge_25_lt_50_stars_ranges'],
    [medium_non_ionizing_peaks,'non_ionizing_ge_25_lt_50_stars_peaks']
]

for identified_regions,mn in meshes:
    if mn not in ['some_ionizing_ranges','non_ionizing_ge_25_lt_50_stars_ranges']:
        continue
    polyDataAccum = vtk.vtkPolyData()

    print("creating "+mn+" mesh with",len(identified_regions),"regions")

    gp = open(rootDir+'output/release/'+mn+'.csv','w')

    for identified_region in identified_regions:
        if mn == 'non_ionizing_ge_25_lt_50_stars_ranges' and identified_region == '79-123':
            continue
        if mn == 'some_ionizing_ranges' and identified_region == '79-149':
            continue
        try:
            print(identified_region,counts[identified_region])
        except:
            print('weird print error')
        gp.write(identified_region+','+str(counts[identified_region])+"\n")
        
        density,subregion = identified_region.split('-')
        fn = rootDir+'output/slices/hot/iso2/iso_'+density+'_percent/region_'+subregion+'.obj'
        if not os.path.isfile(fn):
            print(fn,"does not exist")
        reader = vtk.vtkOBJReader()
        reader.SetFileName(fn)
        reader.Update()
        mesh = reader.GetOutput()

        appendFilter = vtk.vtkAppendPolyData()
        appendFilter.AddInputData(mesh)
        appendFilter.AddInputData(polyDataAccum)
        appendFilter.Update()

        cleanFilter = vtk.vtkCleanPolyData()
        cleanFilter.SetInputData(appendFilter.GetOutput())
        cleanFilter.Update()

        polyDataAccum = cleanFilter.GetOutput()    

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
    writer.SetFilePrefix(rootDir+'output/release/'+mn)
    #writer.SetFilePrefix(rootDir+'output/release_version_2_revised/some_ionizing_peaks')
    writer.SetInput(renWin)
    writer.Write()

    gp.close()