import glob
import os
import itertools
from collections import Counter

# change the path to current because I'm lazy
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# function to split out sections of string
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
path = ''
while path != "quit":
    # request folder
    path  = input('Folder ("quit" to quit): ')

    # get the list of files
    losscounter = Counter({"PERSONNEL": 0})
    for fid in glob.glob(path+'/*.txt'):
        with open(fid) as f:
            text = f.read()
        # split out the losses section
        losses = find_between(text,'Losses:','Current:')
        lossitems = losses.split('\n')
        for i in range(len(lossitems)):
            lossitems[i] = lossitems[i].strip().split(maxsplit=1)
            if len(lossitems[i]) > 1:
                #print(lossitems[i])
                lossitemcounter = Counter({lossitems[i][1]: int(lossitems[i][0])})
                losscounter.update(lossitemcounter)

        #print(lossitems)

    # print the counter items
    for keys, items in losscounter.items():
        print("{:6d} {}".format(items, keys))