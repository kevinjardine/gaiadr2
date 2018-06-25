import math
import os

#config

rootDir = 'd:/projects/astronomy/gaia_dr2/'

#code

# Sample query:

# select designation,l, b, parallax, parallax_over_error, phot_g_mean_mag, bp_rp, priam_flags, teff_val, 
# a_g_val, a_g_percentile_lower, a_g_percentile_upper, e_bp_min_rp_val, e_bp_min_rp_percentile_lower,
# e_bp_min_rp_percentile_upper from gaiadr2.gaia_source 
# where (parallax_over_error > 10) and (parallax >= 0.1) and (parallax < 0.2)

# where I changed the parallax limits 28 times
# they all go in the data/dr2 directory as csv files

starCounts = {'I':{'above':0,'below':0},'II':{'above':0,'below':0},'III':{'above':0,'below':0},'IV':{'above':0,'below':0}}
distanceCounts = {}
allCount = 0
nonNullCount = 0
flagCount = 0
cutCount = 0
bothCutsCount = 0

hotCount = 0
hotNonNullCount = 0
hotFlagCount = 0
hotCutCount = 0
hotBothCutsCount = 0

if not os.path.isdir(rootDir+'output/star_list'):
    os.mkdir(rootDir+'output/star_list')

csv = open(rootDir+'output/star_list/all_stars_0.1.csv','w')
stats = open(rootDir+'output/star_list/all_stats_0.1.txt','w')

directory = rootDir+'data/dr2/'

for fileName in os.listdir(directory):
    if not fileName.endswith(".csv"):
        continue
    fp = open(directory+fileName,'r')
    fieldNames = fp.readline().strip().split(',')
    line = fp.readline()
    while len(line) != 0:
        d = {}
        bits = line.strip().split(',')
        for i in range(0,len(bits)):
            d[fieldNames[i]] = bits[i]
        poe = float(d['parallax_over_error'])
        if poe > 10:
            allCount += 1     
            relMag = float(d['phot_g_mean_mag'])
            ci = float(d['bp_rp'])
            ag = d['a_g_val']
            excess = d['e_bp_min_rp_val']
            flags = d['priam_flags']
            cutFlag = (flags == '100001') or (flags == '100002')
            if cutFlag:
                flagCount += 1
            nonNullCut = (ag != '') and (excess != '')
            if nonNullCut:
                nonNullCount += 1
                ag = float(ag)
                ag_lower = float(d['a_g_percentile_lower'])
                ag_upper = float(d['a_g_percentile_upper'])
                excess = float(excess)
                excess_lower = float(d['e_bp_min_rp_percentile_lower'])
                excess_upper = float(d['e_bp_min_rp_percentile_upper'])

                #note: I extended this cut to include (ag == ag_lower)
                cut1 = (ag == ag_lower) or (ag_upper - ag)/(ag - ag_lower) > 0.4
                cut2 = (ag - ag_lower) < 0.5
                #note: I extended this cut to include (excess == excess_lower)
                cut3 = (excess == excess_lower) or (excess_upper - excess)/(excess - excess_lower) > 0.4
                cut4 = (excess - excess_lower) < 0.3
                cutData = cut1 and cut2 and cut3 and cut4
                if cutData:
                    cutCount += 1
                    if cutFlag:
                        bothCutsCount += 1

                relMag -= ag
                ci -= excess
            else:
                cutFlag = False
                cutData = False

            plx = float(d['parallax'])
            dist = 1000/plx
            m = relMag - 5*(math.log10(dist) - 1)

            glon = float(d['l'])
            glat = float(d['b'])  
            if glat >= 0:
                region = 'above'
            else:
                region = 'below'

            if glon < 90:
                quadrant = 'I'
            elif glon < 180:
                quadrant = 'II'
            elif glon < 270:
                quadrant = 'III'
            else:
                quadrant = 'IV'

            starCounts[quadrant][region] += 1
        
            bin = str(int(round(dist/500)))
            if bin in distanceCounts:
                distanceCounts[bin] += 1
            else:
                distanceCounts[bin] = 1
            cosl = math.cos(glon*math.pi/180)
            sinl = math.sin(glon*math.pi/180)
            cosb = math.cos(glat*math.pi/180)
            sinb = math.sin(glat*math.pi/180)
            xg = dist*cosb*cosl
            yg = dist*cosb*sinl
            zg = dist*sinb

            nonNull = '1' if nonNullCut else '0'
            flag = '1' if cutFlag else '0'
            data = '1' if cutData else '0'

            a = [d['designation'], str(ci), str(xg), str(yg), str(zg), d['l'], d['b'],str(m),d['parallax'],d['parallax_over_error'],d['a_g_val'],d['e_bp_min_rp_val'],nonNull,flag,data]
            s = (','.join(a))+"\n"
            csv.write(s)
        line = fp.readline()
    print(fileName,allCount,bothCutsCount,nonNullCount,flagCount,cutCount)
    fp.close()
csv.close()

stats.write('starCounts: '+str(starCounts)+"\n\n")
stats.write('distanceCounts: '+str(distanceCounts)+"\n")

stats.write('allCount: '+str(allCount)+"\n\n")
stats.write('nonNullCount: '+str(nonNullCount)+"\n\n")
stats.write('flagCount: '+str(flagCount)+"\n\n")
stats.write('cutCount: '+str(cutCount)+"\n\n")
stats.write('bothCutsCount: '+str(bothCutsCount)+"\n\n")

stats.close()