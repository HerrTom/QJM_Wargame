import os
from collections import Counter
from scipy.interpolate import interp1d
from random import random
import yaml

import qjm_interps

# future work I want to do here is to combine the formation_group and 
# formation objects such that any formation can have sub-formations

def make_safe_filename(s):
    def safe_char(c):
        if c == '"':
            return ""
        if c.isalnum():
            return c
        else:
            return ""
    return "".join(safe_char(c) for c in s).rstrip("_")

def ListToFormattedString(alist):
    formatted_list = ['{:}' for item in alist] 
    s = ','.join(formatted_list)
    return s.format(*alist)

class oli_obj():
    def __init__(self):
        self.total = 0
        self.inf = 0
        self.afv = 0
        self.at = 0
        self.arty = 0
        self.ad = 0
        self.air = 0

def DictToText(x):
    txt = ""
    for key, item in x.items():
        txt += "            {:> 6,d}   {:15}\n".format(item,key)
    return txt
    
# generic formation class
class formation():
    def __init__(self, name, equipment, personnel, faction, type, CEV,):
        self.name = name
        self.type = type
        self.equipment = equipment
        self.personnel = personnel
        self.faction = faction
        sefl.CEV = CEV

    def __repr__(self):
        return 'formation({} @{:,.0f})'.format(self.name, self.OLI)
    
    def output(self,path="../database/_gamemaster/working"):
        frm = self
        if hasattr(frm,'equip_list'):
            del frm.equip_list
        os.makedirs(path, exist_ok=True)
        # filter the filename so it's acceptable
        filename = make_safe_filename(self.name)
        # output the yaml file containing the equipment
        with open("{}\\{}.yml".format(path,filename),'w+') as f:
            yaml.dump(self, f, default_flow_style=False)
    
    def SITREP(self,loss_dict={"N/A": 0},activity='Attacking',
               datestr="",location="",writefolder=None):
        # returns a SITREP report
        # skipping ID lines (3-7)
        #datestr = "0400 01 JANUARY 1983"
        situation = activity
        #location = "Berlin"
        losses = DictToText(loss_dict)
        current = DictToText(self.equipment)
        if self.vehicles_base == 0: # deal with divide by zero problems
            self.vehicles_base = 1
        sitrep_string = ("DATE AND TIME {}\n"
                "UNIT          {}\n"
                "ACTIVITY      {}\n"
                "EFFECTIVE     {:.0f}% combat power\n"
                "DISPOSITION   {:.0f}% PERSONNEL | {:.0f}% VEHICLES\n"
                "LOCATION      {}\n"
                "SITUATION\n"
                "              Losses:\n{}\n"
                "              Current:\n{}\n"
                "PERSONNEL:    {:,.0f}\n".format(datestr,self.name,situation,self.OLI/self.OLI_base*100,
                                self.personnel/self.personnel_base*100, self.vehicles/self.vehicles_base*100,
                                location,losses,current,self.personnel))
        if writefolder is not None:
            filename = writefolder + '\\' + make_safe_filename('{} {}'.format(datestr,self.name)) + '.txt'
            with open(filename, 'w+') as f:
                f.write(sitrep_string)
                f.close()
        
        return sitrep_string

    def GetOLI(self,):
        return ("OLI statistics for {}\n"
        "Overall:     {:,.0f}\n"
        "Infantry:    {:,.0f}\n"
        "AFVs:        {:,.0f}\n"
        "Anti-tank:   {:,.0f}\n"
        "Artillery:   {:,.0f}\n"
        "Air defense: {:,.0f}\n"
        "Aircraft:    {:,.0f}\n"
        "No TLI for: {}\n").format(self.name,self.OLI,self.OLI_inf,self.OLI_afv,self.OLI_at,
                                        self.OLI_arty,self.OLI_ad,self.OLI_air,
                                        ListToFormattedString(self.NoTLIData))
    
    def BaseStats(self):
        self.OLI_base = self.OLI
        self.personnel_base = self.personnel
        self.vehicles_base = self.vehicles
    
    def GenOLI(self, equipment_list):
        self.equip_list = equipment_list
        self.OLI        = 0
        self.OLI_inf    = 0 # infantry
        self.OLI_afv    = 0 # tanks
        self.OLI_at     = 0 # anti tank
        self.OLI_arty   = 0 # artillery
        self.OLI_ad     = 0 # air defense
        self.OLI_air    = 0 # aircraft
        
        self.vehicles = 0
        
        self.NoTLIData = list()
        for equip, qty in self.equipment.items():
            try:
                equip_entry = equipment_list.equip_by_name(equip)
                equip_TLI = equip_entry.TLI
                equip_type = equip_entry.type
            except BaseException:
                # print('No equipment entry for {}\n'.format(equip))
                equip_TLI = 0
                self.NoTLIData.append(equip)
                equip_type = None
                pass
            self.OLI += qty * equip_TLI
            # classify the equipment by category
            if equip_type in ["INF", "APC",]:
                self.OLI_inf += qty * equip_TLI
            elif equip_type in ["AFV", "IFV",]:
                self.OLI_afv += qty * equip_TLI
            elif equip_type in ["AT", "SP AT"]:
                self.OLI_at += qty * equip_TLI
            elif equip_type in ["Artillery", "SP Artillery"]:
                self.OLI_arty += qty * equip_TLI
            elif equip_type in ["AD", "SP AD"]:
                self.OLI_ad += qty * equip_TLI
            elif equip_type in ["AIR"]:
                self.OLI_air += qty * equip_TLI
            # while we're at it, let's also calculate the vehicles in the unit
            # classify the equipment by category
            if equip_type in ["APC", "IFV", "AFV", "SP AT", "SP Artillery", "SP AD", "AIR"]:
                self.vehicles += qty
                #print("{}: {}".format(equip,qty))
                
    def casualties(self,power_ratio,mission,day=True,duration=24,exposure=1,pers=None):
        # power_ratio is combat power ratio of friendly to enemy
        # mission is mission string - attack, prepared defence, etc
        # day is boolean - daytime or nighttime
        # duration is hours of combat
        # exposure is percentage of formation engaged 

        # calculate the strength/size factor
        if pers is None:
            factor_size = qjm_interps.casualty_size_factor(self.personnel)
        else:
            factor_size = qjm_interps.casualty_size_factor(pers)
        #op_pts = [1000, 3, 2.5, 1.5, 0.83, 0.6, 0.45, 0.35, 0.25, 0.2, 0.15]
        #op_factor_pts = [0, 0.7, 0.8, 0.9, 1.0 ,1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
        #op_interp = interp1d(op_pts, op_factor_pts, fill_value='extrapolate')
        if mission == 'attack':
            casualty_base = .028
            #factor_opposition = op_interp(power_ratio)
            factor_opposition = qjm_interps.casualty_opposition_factor(power_ratio)
        else:
            casualty_base = .015
            #factor_opposition = op_interp(1/power_ratio)
            factor_opposition = qjm_interps.casualty_opposition_factor(1/power_ratio)
        if day:
            factor_day = 1
        else:
            factor_day = 0.5
        
        base_rate = casualty_base * factor_size * factor_opposition * factor_day * exposure
        casualty_rate = 1-(1-(base_rate))**(duration/24) # 1-(1-R)^d for modifying time based probability, default is per day
        print("Casualty rate: {:.1f}% for {}".format(casualty_rate*100,self.name))
        print("Base daily rate: {:.1f}%".format(base_rate*100))
        print("Factors: base:{} size:{} opp:{} day:{}".format(casualty_base,factor_size,factor_opposition,factor_day))
        # create the losses dictionary
        loss_dict = Counter()
        pers_losses = 0
        # go through the equipment and kill it
        for equip, qty in self.equipment.items():
            try:
                equip_entry = self.equip_list.equip_by_name(equip)
                equip_type = equip_entry.type
                crew = equip_entry.crew
                if equip_type in ['ARM', 'APC', 'IFV']:
                    factor_equipment = 5.4
                elif equip_type in ['SP Artillery']:
                    factor_equipment = 0.5
                elif equip_type in ['Artillery']:
                    factor_equipment = 0.2
                else: # any other weapon
                    factor_equipment = 1
            except: # execption handles nonexistant weapons
                factor_equipment = 1
                crew = 1
                pass
            casualty_rate_adj = casualty_rate * factor_equipment
            losses = 0
            
            for x in range(qty):
                # roll for a kill
                roll = random() # roll a random float
                if roll <= casualty_rate_adj:
                    losses += 1
                    pers_losses += crew
            loss_dict.update({equip: -losses})
        # add the generated loss dictionary to the 
        temp_equip = Counter(self.equipment)
        temp_equip.update(loss_dict)
        self.equipment = dict(temp_equip)
        self.personnel += -pers_losses
        loss_dict.update({"PERSONNEL": -pers_losses})
        
        # after killing everything, reevaluate the OLI
        self.GenOLI(self.equip_list)
        
        return dict(loss_dict)
        
    def generate_formation(self, form_list):
        # creates a formation from the group definition
        # run through the list of formations
        equipment = dict()
        personnel = 0
        for name in self.formations:
            form = form_list.formation_by_name(name)
            equipment = Counter(equipment) + Counter(form.equipment)
            personnel += form.personnel
        new_formation = formation(self.name, dict(equipment), personnel)
        return new_formation
            
# class that allows a list of formations to be searched
class formation_list():
    def __init__(self, formations):
        self.names = list()
        self.forms = list()
        self.factions = list()
        for form in formations:
            self.names.append(form.name)
            self.forms.append(form)
            self.factions.append(form.faction)

    def formation_by_name(self, name_to_find):
        return self.forms[self.names.index(name_to_find)]
    
    def pers_by_names(self,name_list):
        pers = 0
        if name_list is str: # handle if there is only a string input
            name_list = [name_list]
        for name in name_list:
            formation = self.formation_by_name(name)
            pers += formation.personnel
        return pers
    
    def vehicles_by_names(self,name_list,equip_db):
        vehicles = 0
        if name_list is str: # handle if there is only a string input
            name_list = [name_list]
        for name in name_list:
            formation = self.formation_by_name(name)
            for equip, qty in formation.equipment.items():
                try:
                    equip_entry = equip_db.equip_by_name(equip)
                    equip_type = equip_entry.type
                except BaseException:
                    equip_type = None
                    pass
                # classify the equipment by category
                if equip_type in ["APC", "IFV", "AFV", "SP AT", "SP Artillery", "SP AD"]:
                    vehicles += qty
                    #print("{}: {}".format(equip,qty))
        return vehicles
        
    def oli_by_names(self,name_list):
        OLI = oli_obj() # inits oli value to zero
        if name_list is str: # handle if there is only a string input
            name_list = [name_list]
        for name in name_list:
            form = self.formation_by_name(name)
            CEV = form.CEV
            OLI.total += form.OLI
            OLI.inf += form.OLI_inf
            OLI.afv += form.OLI_afv
            OLI.at += form.OLI_at
            OLI.arty += form.OLI_arty
            OLI.ad += form.OLI_ad
            OLI.air += form.OLI_air
        return OLI
    
    def find_no_entries(self,):
        no_equip = []
        for form in self.forms:
            for itm in form.NoTLIData:
                no_equip.append(itm)
        return list(set(no_equip))

    def __repr__(self):
        return 'formation_list({})'.format(self.names)

        
# class that allows formations to be combined
class formation_group():
    def __init__(self, name, formations, faction, type,):
        self.name = name
        self.formations = formations
        self.faction = faction
        self.type = type

    def __repr__(self):
        return 'formation_group({})'.format(self.name)

    def generate_formation(self, form_list):
        # creates a formation from the group definition
        # run through the list of formations
        equipment = dict()
        personnel = 0
        CEV = 0
        for name in self.formations:
            form = form_list.formation_by_name(name)
            equipment = Counter(equipment) + Counter(form.equipment)
            personnel += form.personnel
        new_formation = formation(self.name, dict(equipment), personnel, self.faction, self.type,
                                    CEV)
        return new_formation