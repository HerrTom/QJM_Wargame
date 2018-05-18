import os, glob

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# folder categories and their mappings
folders = {"UK": "bri",
            "BRD": "brd",
            "DDR": "ddr",
            "FRA": "fra",
            "USSR": "sov",
            "USA": "usa",}

files = glob.glob("*.txt")

for file in files:
    for key, folder in folders.items():
        if key in file:
            print("Moved {} to ./{}/".format(file,folder))
            try:
                os.mkdir(folder)
            except OSError:
                pass
            os.rename(file,"{}/{}".format(folder,file))