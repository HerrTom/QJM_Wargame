import math
import qjm_interps
import inspect

global Di
Di = 5000 # dispersion factor - hardcoded for now

def what(var,):
    """
    Gets the name of var. Does it from the out most frame inner-wards.
    :param var: variable to get name from.
    :return: string
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]

def printvars(*argv):
    for arg in argv:
        print(what(arg),arg)

# Todo:
# - Create a master Equipment class that contains the GenTLI function
# - GenTLI function then becomes dynamic and will ignore (?) nonexistent values

# common parsing functions
def armour_factor(entry):
    # parse the fire control string
    if entry.armour.lower() == 'aluminium':
        ARMF = 0.7
    elif entry.armour.lower() == 'modern reactive':
        ARMF = 2.1
    elif entry.armour.lower() == 'reactive':
        ARMF = 1.6
    elif entry.armour.lower() == 'composite':
        ARMF = 1.5
    elif entry.armour.lower() == 'early composite':
        ARMF = 1.3
    else:
        ARMF = 1
    return ARMF

def fire_control_factor(entry):
    # parse the fire control string
    if entry.fire_control.lower() == 'stereoscopic rangefinder':
        FCE = 0.9
    elif entry.fire_control.lower() == 'laser rangefinder':
        FCE = 1.5
    elif entry.fire_control.lower() == 'early thermal optics':
        FCE = 1.8
    elif entry.fire_control.lower() == 'thermal optics':
        FCE = 2
    else:
        FCE = 0.5
    return FCE
    

def fire_control_factor_airdef(entry):
    # parse the fire control string for air defense vehicles
    if entry.fire_control.lower() == 'optical':
        FCE = 0.9
    elif entry.fire_control.lower() == 'small radar':
        FCE = 1.3
    elif entry.fire_control.lower() == 'medium radar':
        FCE = 1.6
    elif entry.fire_control.lower() == 'large radar':
        FCE = 2
    else:
        FCE = 0.5
    return FCE
    
# class that allows a list of equipment to be easily contained and searched
class equip_list():
    def __init__(self, list_of_equips):
        self.names = list()
        self.equips = list()
        self.types = list()
        for entry in list_of_equips:
            self.names.append(entry.name)
            self.equips.append(entry)
            self.types.append(entry.type)

    def equip_by_name(self, name_to_find):
        return self.equips[self.names.index(name_to_find)]
        
    def names_by_types(self,types):
        #   types here is a list of filters
        return [nm for nm,tp in zip(self.names,self.types) if tp in types]


class equipment_inf():
    type = "INF"
    def __init__(self, name, weapons, ammo_store, ammo,  crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # ASE is just the MBE for infantry weapons
            if i == 0:
                weap_ASE = 1
                weap_RF = weapdb.weapons[idx].RF
            elif i == 1:
                weap_ASE = 0.5
            elif i == 3:
                weap_ASE = 0.33
            else:
                weap_ASE = 1 / i
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

        self.TLI = WEAP

class equipment_infat():
    type = "AT"
    def __init__(self, name, weapons, ammo_store, ammo,  crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # ASE is just the MBE for infantry weapons
            if i == 0:
                weap_ASE = 1
                weap_RF = weapdb.weapons[idx].RF
            elif i == 1:
                weap_ASE = 0.5
            elif i == 3:
                weap_ASE = 0.33
            else:
                weap_ASE = 1 / i
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

        self.TLI = WEAP

class equipment_infarty():
    type = "Artillery"
    def __init__(self, name, weapons, ammo_store, ammo,  crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # ASE is just the MBE for infantry weapons
            if i == 0:
                weap_ASE = 1
                weap_RF = weapdb.weapons[idx].RF
            elif i == 1:
                weap_ASE = 0.5
            elif i == 3:
                weap_ASE = 0.33
            else:
                weap_ASE = 1 / i
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

        self.TLI = WEAP
        
class equipment_infad():
    type = "AD"
    def __init__(self, name, weapons, ammo_store, ammo,  crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # ASE is just the MBE for infantry weapons
            if i == 0:
                weap_ASE = 1
                weap_RF = weapdb.weapons[idx].RF
            elif i == 1:
                weap_ASE = 0.5
            elif i == 3:
                weap_ASE = 0.33
            else:
                weap_ASE = 1 / i
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

        self.TLI = WEAP
        
class equipment_spat():
    type = "SP AT"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew, armour, amphibious):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.amphibious = False
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5 / 2
        # parse the armour value
        ARMF = armour_factor(self)
        #FCE = fire_control_factor(self)
        RFE = 1
        ASE = 1
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * ASE * AME * CL

class equipment_spad():
    type = "SP AD" # self propelled air defense
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew, armour,
                    FCE, amphibious):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.amphibious = amphibious
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5 / 2
        # parse the armour value
        ARMF = armour_factor(self)
        FCE = fire_control_factor_airdef(self)
        RFE = 1
        ASE = 1
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL
        
class equipment_afv():
    type = "AFV"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew, armour,
                FCE, amphibious,):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.amphibious = amphibious
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        # parse the armour value
        ARMF = armour_factor(self)
        FCE = fire_control_factor(self)
        RFE = 1
        ASE = 1
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL

        #print('---',self.name,'---')
        #printvars(WEAP,MOF,RA,PF,ARMF,RFE,FCE,ASE,AME,CL)
        #print('TLI',self.TLI)

class equipment_sparty():
    type = "SP Artillery"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew, armour,
                amphibious,):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.amphibious = amphibious
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5 /2 # divided by two for assault guns
        # parse the armour value
        ARMF = armour_factor(self)
        RFE = 1
        ASE = 1
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * ASE * AME * CL

class equipment_ifv():
    type = "IFV"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew,
            armour, FCE, squad, amphibious,):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.amphibious = amphibious
        self.squad = squad
        self.squad_weaps = [] # blank for now
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
                print(self.name, weapname, weap_ASE)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

            
        # weapons from squad
        WEAP_SQUAD = self.squad
        
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        ARMF = armour_factor(self)
        FCE = fire_control_factor(self)
        RFE = 1
        ASE = 1
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1
        self.TLI = (((WEAP) * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL +WEAP_SQUAD
        
class equipment_apc():
    type = "APC"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew,
            armour, squad, amphibious):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.armour = armour
        self.amphibious = amphibious
        self.squad = squad
        self.squad_weaps = [] # blank for now
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weap_RF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
                pass
            WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di 

            
        # weapons from squad
        WEAP_SQUAD = self.squad
        
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        ARMF = armour_factor(self)
        AME = 1
        if self.amphibious:
            AME = 1.1
        CL = 1
        self.TLI = (((WEAP) * MOF * RA) + PF * ARMF) * AME * CL +WEAP_SQUAD

class equipment_aircraft():
    type = "AIR"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, ammo,  crew, ceiling):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.ammo = ammo
        self.crew = crew
        self.ceiling = ceiling
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        #print("WEAPS -",self.name)
        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            # try the ammo supply factor
            try:
                weap_ASE = qjm_interps.ASE(self.ammo[i] / weapdb.weapons[idx].RF)
            except:
                if i == 0:
                    weap_ASE = 1
                    weapRF = weapdb.weapons[idx].RF
                elif i == 1:
                    weap_ASE = 0.5
                elif i == 3:
                    weap_ASE = 0.33
                else:
                    weap_ASE = 1 / i
            if weapdb.weapons[idx].type == "Automatic gun":
                WEAP += weapdb.weapons[idx].TLI * weap_ASE / Di * 0.25 # all aircraft weapons degraded by .25
            else: # if it's not a gun or automatic gun, then ammo is the quantity of weapons
                WEAP += weapdb.weapons[idx].TLI / Di * 0.25 * math.log(2*self.ammo[i]-1)  # all aircraft weapons degraded by .25
            #print("{} {:,.0f}".format(weapdb.weapons[idx].name,weapdb.weapons[idx].TLI))
            #WEAP += weapdb.weapons[idx].TLI / Di * factor * 0.25 # all aircraft weapons degraded by .25
            #WEAP += weapdb.weapons[idx].TLI / Di * 0.25 # all aircraft weapons degraded by .25 - remove degradation of redundant weapons?
            
        MOF = 0.15 * (500 + 0.1*(max(0,self.speed-500)) + 0.01*(max(0,self.speed-1500)))**0.5 # max clips the value at zero
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5 / 2 # half PF for aircraft
        # parse the armour value
        FCE = 1
        RFE = 1
        ASE = 1
        CL = 1 + 0.02*min(0,(self.ceiling-30000)/1000) + 0.005*max(0,(self.ceiling-30000)/1000) # +.005 for each 1k ft above 30k, -0.02 for each 1k ft below 30k

        #print("Aircraft ",self.name,"| WEAP",WEAP,"| CL",CL,"| MOF",MOF,"| RA",RA)

        self.TLI = ((WEAP * MOF * RA) + PF) * RFE * FCE * ASE * CL

        #print('---',self.name,'---')
        #printvars(WEAP,MOF,RA,PF,ARMF,RFE,FCE,ASE,AME,CL)
        #print('TLI',self.TLI)