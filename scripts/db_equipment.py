import qjm_interps

global Di
Di = 4000 # dispersion factor - hardcoded for now

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

# class that allows a list of equipment to be easily contained and searched
class equip_list():
    def __init__(self, list_of_equips):
        self.names = list()
        self.equips = list()
        for entry in list_of_equips:
            self.names.append(entry.name)
            self.equips.append(entry)

    def equip_by_name(self, name_to_find):
        return self.equips[self.names.index(name_to_find)]


class equipment_inf():
    type = "INF"
    def __init__(self, name, weapons, ammo_store, crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            if i == 0:
                factor = 1
                weapRF = weapdb.weapons[idx].RF
            elif i == 1:
                factor = 0.5
            elif i == 3:
                factor = 0.33
            else:
                factor = i / 4
            WEAP += weapdb.weapons[idx].TLI / Di

        self.TLI = WEAP

class equipment_infat():
    type = "INF AT"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, crew):
        self.name = name
        self.weapons = weapons
        self.ammo_store = ammo_store
        self.crew = crew
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            if i == 0:
                factor = 1
                weapRF = weapdb.weapons[idx].RF
            elif i == 1:
                factor = 0.5
            elif i == 3:
                factor = 0.33
            else:
                factor = i / 4
            WEAP += weapdb.weapons[idx].TLI / Di

        self.TLI = WEAP

class equipment_afvat():
    type = "AFV AT"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, crew, armour, FCE):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            if i == 0:
                factor = 1
                weapRF = weapdb.weapons[idx].RF
            elif i == 1:
                factor = 0.5
            elif i == 3:
                factor = 0.33
            else:
                factor = i / 4
            WEAP += weapdb.weapons[idx].TLI / Di
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        # parse the armour value
        ARMF = armour_factor(self)
        FCE = fire_control_factor(self)
        RFE = 1
        ASE = qjm_interps.ASE(self.ammo_store / weapRF)
        AME = 1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL
        
class equipment_afv():
    type = "AFV"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, crew, armour, FCE):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):
        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            if i == 0:
                factor = 1
                weapRF = weapdb.weapons[idx].RF
            elif i == 1:
                factor = 0.5
            elif i == 3:
                factor = 0.33
            else:
                factor = i / 4
            WEAP += weapdb.weapons[idx].TLI / Di
            
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        # parse the armour value
        ARMF = armour_factor(self)
        FCE = fire_control_factor(self)
        RFE = 1
        ASE = qjm_interps.ASE(self.ammo_store / weapRF)
        AME = 1
        CL = 1

        self.TLI = ((WEAP * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL


class equipment_pc():
    type = "PC"
    def __init__(self, name, weapons, range, weight, speed, ammo_store, crew,
            armour, FCE, squad):
        self.name = name
        self.weapons = weapons
        self.range = range
        self.weight = weight
        self.speed = speed
        self.ammo_store = ammo_store
        self.crew = crew
        self.armour = armour
        self.fire_control = FCE
        self.squad = squad
        self.nation = ""

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self, weapdb):

        # get the weapons
        WEAP = 0

        for i, weapname in enumerate(self.weapons):
            idx = weapdb.names.index(weapname)
            if i == 0:
                factor = 1
                weapRF = weapdb.weapons[idx].RF
            elif i == 1:
                factor = 0.5
            elif i == 3:
                factor = 0.33
            else:
                factor = i / 4
            WEAP += weapdb.weapons[idx].TLI / Di

            
        # weapons from squad
        WEAP_SQUAD = self.squad
        
        MOF = 0.15 * (self.speed)**0.5
        RA = 0.08 * (self.range)**0.5
        PF = self.weight / 4 * (2 * self.weight)**0.5
        ARMF = armour_factor(self)
        FCE = fire_control_factor(self)
        RFE = 1
        ASE = qjm_interps.ASE(self.ammo_store / weapRF)
        AME = 1
        CL = 1
        self.TLI = (((WEAP+WEAP_SQUAD) * MOF * RA) + PF * ARMF) * RFE * FCE * ASE * AME * CL

