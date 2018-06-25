rootDir = 'd:/projects/astronomy/gaia_dr2/'

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

for density in range(5,100):
    fn = rootDir+'output/slices/hot/csv2/stars_in_regions_'+str(density)+'.csv'
    fp = open(fn,'r')
    line = fp.readline()
    print(density)
    while len(line) != 0:
        bits = line.strip().split(',')
        if len(bits) > 3:
            name, colourIndex, xg, yg, zg, glon, glat, m, plx,plx_over_err,extinction,excess,nonNullCut,flagCut,dataCut,region = bits
            slug = str(density)+'-'+region
            if slug in regions:
                if float(colourIndex) < -0.2:
                    if slug not in region_count:
                        region_count[slug] = 0
                    region_count[slug] += 1
                
        line = fp.readline()
    fp.close()

fn = rootDir+'output/release/dr2_ionizing_stars_per_range.csv'
gp = open(fn,'w')
for slug in region_count:
    gp.write(slug+','+str(region_count[slug])+"\n")
gp.close()
