import qjm_interps

def signed_sqrt(x):
    if x >= 0:
        return x**0.5
    else:
        return -(-x) ** 0.5

        
# class that allows a list of weapons to be easily contained and searched
class weapon_list():
    def __init__(self, weapons):
        self.names = list()
        self.weapons = list()
        for weap in weapons:
            self.names.append(weap.name)
            self.weapons.append(weap)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,self.names)
        
    def weap_by_name(self, name_to_find):
        return self.weapons[self.names.index(name_to_find)]

class weapon():
    type = "No type"
    def __init__(self,):
        self.name = ""
    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

class weapon_gun():
    type = "Gun"
    def __init__(
            self,
            name,
            range,
            accuracy,
            rie,
            barrels,
            calibre,
            muzzle_vel,
            ammo):
        self.name = name
        self.range = range
        self.accuracy = accuracy
        self.rie = rie
        self.barrels = barrels
        self.calibre = calibre
        self.muzzle_vel = muzzle_vel
        self.ammo = ammo
        
        # if generated using __init__ also generate the TLI
        self.GenTLI()

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        RF = qjm_interps.RF_From_Calibre(self.calibre)
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * 0.1 * (self.calibre)**0.5
        if RN_MV > RN_Range:
            RN = RN_MV
        else:
            RN = (RN_Range + RN_MV) / 2
        A = self.accuracy
        RL = 1
        SME = 1
        MCE = 1
        AE = 1
        MBE = qjm_interps.MBE(self.barrels)
        self.RF = RF
        self.TLI = RF * PTS * RIE * RN * A * RL * SME * MCE * AE * MBE
        
class weapon_autogun():
    type = "Automatic gun"
    def __init__(
            self,
            name,
            range,
            accuracy,
            rie,
            rof,
            rf_multiple,
            barrels,
            calibre,
            muzzle_vel,
            ammo):
        self.name = name
        self.range = range
        self.accuracy = accuracy
        self.rie = rie
        self.rate_of_fire = rof
        self.rf_multiple = rf_multiple
        self.barrels = barrels
        self.calibre = calibre
        self.muzzle_vel = muzzle_vel
        self.ammo = ammo
        
        # if generated using __init__ also generate the TLI
        self.GenTLI()

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        RF = self.rate_of_fire * self.rf_multiple
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * 0.1 * (self.calibre)**0.5
        if RN_MV > RN_Range:
            RN = RN_MV
        else:
            RN = (RN_Range + RN_MV) / 2
        A = self.accuracy
        RL = 1
        SME = 1
        MCE = 1
        AE = 1
        MBE = qjm_interps.MBE(self.barrels)
        self.RF = RF
        self.TLI = RF * PTS * RIE * RN * A * RL * SME * MCE * AE * MBE

class weapon_atgm():
    type = "ATGM"
    def __init__(
            self,
            name,
            range,
            rie,
            barrels,
            calibre,
            muzzle_vel,
            ammo,
            min_range,
            penetration,
            guidance,
            enhancement):
        self.name = name
        self.range = range
        self.rie = rie
        self.barrels = barrels
        self.calibre = calibre
        self.muzzle_vel = muzzle_vel
        self.ammo = ammo
        self.min_range = min_range
        self.penetration = penetration
        self.guidance = guidance
        self.enhancement = enhancement
        
        # if generated using __init__ also generate the TLI
        self.GenTLI()

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        RF = qjm_interps.RF_From_Calibre(self.calibre)
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * 0.1 * (self.calibre)**0.5
        if RN_MV > RN_Range:
            RN = RN_MV
        else:
            RN = (RN_Range + RN_MV) / 2
        # derive accuracy from guidance value
        acc = {'SACLOS wire day': 1.6,
               'SACLOS wire day/night': 1.7,
               'SACLOS radio': 1.7,
               'LOSLBR': 1.8,
               'F&F': 1.9}
        A = acc[self.guidance]
        RL = 1
        SME = 1
        GE = 2 # guided weapons have a bonus effect
        MCE = 1
        AE = 1
        MBE = qjm_interps.MBE(self.barrels)
        self.RF = RF
        MRN = 1 - 0.19 * ((self.min_range - 100) / 100)
        PEN = 1 + 0.01 * signed_sqrt(self.penetration - 500)
        VEL = 1 + .001 * (self.muzzle_vel - 400)
        EN = self.enhancement
        self.TLI = RF * PTS * RIE * RN * A * RL * \
            SME * MCE * AE * MBE * MRN * PEN * VEL * EN * GE

class weapon_aam():
    type = "AAM"
    def __init__(
            self,
            name,
            range,
            barrels,
            calibre,
            muzzle_vel,
            ammo,
            min_range,
            guidance,
            enhancement):
        self.name = name
        self.range = range
        self.rie = 1
        self.barrels = barrels
        self.calibre = calibre
        self.muzzle_vel = muzzle_vel
        self.ammo = ammo
        self.min_range = min_range
        self.guidance = guidance
        self.enhancement = enhancement
        
        # if generated using __init__ also generate the TLI
        self.GenTLI()

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        RF = qjm_interps.RF_From_Calibre(self.calibre)
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * 0.1 * (self.calibre)**0.5
        if RN_MV > RN_Range:
            RN = RN_MV
        else:
            RN = (RN_Range + RN_MV) / 2
        # derive accuracy from guidance value
        acc = {'Optical': 1,
               'BR': 1.2,
               'IR': 1.8,
               'SARH': 1.5,
               'ARH': 2.0}

        A = acc[self.guidance]
        RL = 1
        SME = 1
        GE = 2 # guided weapons have a bonus effect
        MCE = 1
        AE = 1
        MBE = qjm_interps.MBE(self.barrels)
        self.RF = RF
        MRN = 1 - 0.19 * ((self.min_range - 100) / 100)
        VEL = 1 + .001 * (self.muzzle_vel - 400)
        EN = self.enhancement
        self.TLI = RF * PTS * RIE * RN * A * RL * \
            SME * MCE * AE * MBE * MRN * VEL * EN * GE


class weapon_bomb():
    type = "Bomb"
    def __init__(
            self,
            name,
            accuracy,
            calibre,
            ammo):
        self.name = name
        self.accuracy = accuracy
        self.calibre = calibre
        self.ammo = ammo
        
        # if generated using __init__ also generate the TLI
        self.GenTLI()

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        calibre_corrected = qjm_interps.Calibre_From_Weight(self.calibre)
        RF = 1
        PTS = qjm_interps.PTS_From_Calibre(calibre_corrected)
        RIE = 1
        RN = 1
        A = self.accuracy
        RL = 1
        SME = 1
        MCE = 1
        AE = 1
        MBE = 1
        self.RF = RF
        self.TLI = RF * PTS * RIE * RN * A * RL * SME * MCE * AE * MBE