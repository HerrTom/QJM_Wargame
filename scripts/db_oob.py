import yaml
import os
import glob

from pubsub import pub

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
        self.load_gm_formations()
    
    def update_data(self,):
        self.load_weaps()
        self.load_equip()
        self.load_formations()
        self.load_groups()
        self.load_gm_formations()
    
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
            # only run the base stats if they do not exist
            if not hasattr(self.forms[-1],'personnel_base'):
                self.forms[-1].BaseStats()
        
        self.forms_db = db_formation.formation_list(self.forms)
        
    def load_gm_formations(self,path="../database/_gamemaster/formations"):
        # Load the formation elements
        path = path+'/**/*.yml'
        self.gm_forms = []
        for fid in glob.glob(path, recursive=True):
            with open(fid) as f:
                self.gm_forms.append(yaml.load(f))
            self.gm_forms[-1].GenOLI(self.equip_db)
            # only run the base stats if they do not exist
            if not hasattr(self.gm_forms[-1],'personnel_base'):
                self.gm_forms[-1].BaseStats()
        self.gm_forms_db = db_formation.formation_list(self.gm_forms)
    
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
        # run through the formations and print info
        no_equip = []
        for form in oob.forms:
            print(form.GetOLI())
            # demo the personnel counter and vehicle counter
            nm = form.name
            pers = oob.forms_db.pers_by_names([nm])
            veh = oob.forms_db.vehicles_by_names([nm],oob.equip_db)
            print("{} has {} personnel and {} vehicles\n *****\n".format(nm,pers,veh))
        oob.load_gm_formations("../database/_gamemaster/formations/")
        for form in oob.gm_forms:
            for itm in form.NoTLIData:
                no_equip.append(itm)
        print("No equipment for gm_forms items:")
        print(list(set(no_equip)))