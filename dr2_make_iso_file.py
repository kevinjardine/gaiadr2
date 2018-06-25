#config

rootDir = 'd:/projects/astronomy/gaia_dr2/'

#code

fn = rootDir+'output/slices/hot/structure/structure_tab_iso_5.csv'
fp = open(fn,'r')
line = fp.readline()

regions = {}

while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        iso2,region2,starCount,occurrence,iso1,region1 = bits
        if iso2 not in regions:
            regions[iso2] = {}
        regions[iso2][region2] = [starCount,iso1,region1]
    line = fp.readline()

fp.close()

fn = rootDir+'output/slices/hot/structure/structure_tab_iso_5_full.csv'
gp = open(fn,'w')

iso = '5'
print(iso)
fn = rootDir+'output/slices/hot/csv2/regions_'+iso+'.csv'
fp = open(fn,'r')
line = fp.readline()

while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        region,polys,regionLength,cx,cy,cz,xmin,xmax,ymin,ymax,zmin,zmax,count = bits
        gp.write((',').join([iso,region,cx,cy,cz,count,'',''])+"\n")
    line = fp.readline()
fp.close()


for iso in range(6,100):
    iso = str(iso)
    print(iso)
    fn = rootDir+'output/slices/hot/csv2/regions_'+iso+'.csv'
    fp = open(fn,'r')
    line = fp.readline()

    while len(line) != 0:
        bits = line.strip().split(',')
        if len(bits) > 1:
            region,polys,regionLength,cx,cy,cz,xmin,xmax,ymin,ymax,zmin,zmax,count = bits
            if region in regions[iso]:
                gp.write((',').join([iso,region,cx,cy,cz]+regions[iso][region])+"\n")
        line = fp.readline()
    fp.close()
gp.close()
