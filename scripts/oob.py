import yaml
import os
import glob

# import custom scripts
import db_formation
import db_weapons
import db_equipment

# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# class that holds all of the database files
class oob_db():
    def __init__(self,):
        # reference main entities to use in other areas:
        #   weaps_db
        #   equip_db
        #   forms_db
        self.load_weaps()
        self.load_equip()
        self.load_formations()
        self.load_groups()
    
    def update_data(self,):
        self.load_weaps()
        self.load_equip()
        self.load_formations()
        self.load_groups()
    
    def load_weaps(self,):
        # load in the weapons
        # use of recursive=True with /**/ notation allows searching subdirs
        self.weaps = []
        for fid in glob.glob('../database/weapons/**/*yml', recursive=True):
            with open(fid) as f:
                self.weaps.append(yaml.load(f))
            self.weaps[-1].GenTLI()
        # create the weapon database
        self.weaps_db = db_weapons.weapon_list(self.weaps)
        
    def load_equip(self,):
        # load in the equipment
        self.equip = []
        for fid in glob.glob('../database/equipment/**/*yml', recursive=True):
            with open(fid) as f:
                self.equip.append(yaml.load(f))
                self.equip[-1].GenTLI(self.weaps_db)
        self.equip_db = db_equipment.equip_list(self.equip)
    
    def load_formations(self,):
        # Load the formation elements
        self.forms = []
        for fid in glob.glob('../database/formations/**/*.yml', recursive=True):
            with open(fid) as f:
                self.forms.append(yaml.load(f))
            self.forms[-1].GenOLI(self.equip_db)
        
        self.forms_db = db_formation.formation_list(self.forms)
    
    def load_groups(self,):
        # Load the formation groups
        self.groups = []
        for fid in glob.glob('../database/groups/**/*.yml', recursive=True):
            with open(fid) as f:
                self.groups.append(yaml.load(f))
        # now generate new formations for each group
        for grp in self.groups:
            new_formation = grp.generate_formation(self.forms_db)
            with open('../database/new_formations/{}.yml'.format(grp.name), 'w+') as f:
                yaml.dump(new_formation, f, default_flow_style=False)

# if this is run on its own, lets grab all the data it loads
if __name__ == "__main__":
        oob = oob_db()