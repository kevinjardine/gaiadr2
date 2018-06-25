import json
import copy
rootDir = 'd:/projects/astronomy/gaia_dr2/'

def processLine(line):
    #print(line)
    label_bits = line.split('[')
    if len(label_bits) > 1:
        label_bits2 = label_bits[1].split(']')
        peakName = label_bits2[0].replace('_',' ')
    else:
        peakName = ''
    bits = label_bits[0].split(':')
    structs = []
    maxCount = 0
    for i in range(0,len(bits)-1):
        parts = bits[i].split(' ')
        print(parts)
        if len(parts[0]) > 0 and parts[0][0] == 'T':
            iso, region = parts[1].split('-')
            count = parts[2][1:]
        else:
            iso, region = parts[3].split('-')
            count = parts[4][1:]
        if maxCount == 0:
            maxCount = count
        if int(count) >= 5:
            structs.append({'iso':iso, 'region':region, 'size':count, 'name':peakName, 'children':[]})
    return structs

def addLeaf(trunk,leaf):
    if len(trunk['children']) == 0:
        trunk['children'].append(leaf)
    else:
        newTrunk = addLeaf(trunk['children'][-1],leaf)
        trunk['children'][-1] = newTrunk
    return trunk
    
def process(done,node,toDo):    
    if len(toDo) == 0:
        return done, []
    next = toDo[0]
    if int(next['iso']) > int(node['iso']):
        done = addLeaf(done,node)   
    elif int(next['iso']) == int(node['iso']):
        done['children'].append(node)
    else:
       done.append(node)

def countTabs(line):
    for i in range(0,len(line)):
        if line[i] != '\t':
            return i

def getChildren(indent,lines,c):
    
    children = []
    if len(lines) == 0:
        return lines, children
    line = lines[0]
    curIndent = countTabs(line)       
    
    while len(lines) > 0:
        line = lines[0]
        
        curIndent = countTabs(line)
        if curIndent < indent:
            return lines, children
        print(c,indent,curIndent,line) 
        lines = lines[1:]
        result = processLine(line)
        startItem = result[1]
        newResult = result[0:1]+result[2:]
        if curIndent > indent:
            lines, newChildren = getChildren(curIndent,lines,c+1)
        else:
            newChildren = []
        children.append({startItem:newResult,'children':newChildren})
        indent = curIndent
        #print(children)
    return lines, children

def build(slug,parents):
    if slug in parents:
        result = []
        childSize1 = 0
        for node in parents[slug]:
            slug2 = node['iso']+'-'+node['region']
            nodeSize = int(node['size'])
            childSize1 += nodeSize
            children, childSize2 = build(slug2,parents)
            node['children'] = children
            result.append(node)
        return result, childSize1
    else:
        return [], 0

def flatten(struct):
    if 'children' in struct:
        node = copy.deepcopy(struct)
        while ('children' in node) and (len(node['children']) == 1):
            node = node['children'][0]
        if 'children' in node:
            newChildren = []
            for child in node['children']:
                newChildren.append(flatten(child))
            struct['children'] = newChildren
    return struct

structure = {}
top = {}
topItem = ''
all = {}
collecting = False
structureFile = rootDir+'output/slices/hot/structure/structure_tab_iso_5.txt'
fp = open(structureFile,'r')
lines = fp.readlines()
fp.close()
all = []
for line in lines:
    all += processLine(line.strip())
done = {'siblings':[],'children':[]}
parents = {}
above = {'4':'top'}

slug = 'top'
for node in all:
    #print(node['iso'], node['region'],iso)
    slug = node['iso']+'-'+node['region']
    above[node['iso']] = slug
    parent_slug = above[str(int(node['iso'])-1)]
     
    if parent_slug not in parents:
        parents[parent_slug] = []
    parents[parent_slug].append(node)

children, count = build('top', parents)
struct = flatten({'name':'Main concentration', 'iso':'4','size':count,'children':children})

fp = open('D:/xampp/htdocs/regions/dr2_5.json','w')
fp.write(json.dumps(struct))
fp.close()


