import vtk
import math
import sys

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
                leaves += [b]
    return leaves
    

rootDir = 'd:/projects/astronomy/gaia_dr2/'

leaves = {}
sub_regions = {}
regions = set()
region_data = []
start_density = 77
maximum_stars = 2000
#star_count_min = 25
# star_count_min = 30
#star_count_min = 50
star_count_min = 5
leaf_star_count_min = 50
star_count_prune = 20
labels = {}
centres = {}
counts = {}
sunPosition = [1008.97,998.96,199.96]

plateaus = []
top_level = set()

fn = rootDir+'output/slices/hot/structure/structure_tab_iso_5_full.csv'
fp = open(fn,'r')
line = fp.readline()
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        iso,region,cx,cy,cz,starCount,iso1,region1 = bits
        slug = iso+'-'+region
        if ((int(iso) < start_density) and (int(starCount) >= maximum_stars)) or ((int(iso) > start_density) and (int(starCount) > 560 )):
            plateaus.append(slug)
        centres[slug] = [cx,cy,cz]
        counts[slug] = int(starCount)
        if iso1 != '':
            slug1 = iso1+'-'+region1
            if slug1 not in sub_regions:
                sub_regions[slug1] = []
            sub_regions[slug1].append(slug)
        else:
            top_level.add(slug)
    line = fp.readline()
fp.close()

print(plateaus)
print ('top level',top_level)
print('plateaus',len(plateaus))
ranges = []
for slug in plateaus:
    if slug in sub_regions:
        for slug2 in sub_regions[slug]:
            if slug2 not in plateaus:
                if slug == '8-835' and counts[slug2] >= 25:
                    print('in 8',slug2)
                ranges.append(slug2)

for slug in top_level:
    if slug not in plateaus:
        ranges.append(slug)

gp = open(rootDir+'output/release/ranges.csv','w')

for region in ranges:
    if region != '77-20':
        gp.write(region +','+str(counts[region])+"\n")

gp.close()