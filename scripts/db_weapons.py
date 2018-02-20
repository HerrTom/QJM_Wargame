import qjm_interps

def signed_sqrt(x):
    if x >= 0:
        return x**0.5
    else:
        return -(-x) * 0.5

        
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


class weapon_gun():
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

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        # RF - if empty use calibre
        if self.rate_of_fire is None:
            RF = qjm_interps.RF_From_Calibre(self.calibre)
        else:
            RF = self.rate_of_fire * self.rf_multiple
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * (0.1 * self.calibre)**0.5
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
            ammo,
            min_range,
            penetration,
            guidance,
            enhancement):
        self.name = name
        self.range = range
        self.rie = rie
        self.rate_of_fire = rof
        self.rf_multiple = rf_multiple
        self.barrels = barrels
        self.calibre = calibre
        self.muzzle_vel = muzzle_vel
        self.ammo = ammo
        self.min_range = min_range
        self.penetration = penetration
        self.guidance = guidance
        self.enhancement = enhancement

    def __repr__(self):
        return '{}({} @{:,.0f})'.format(self.__class__.__name__,self.name, self.TLI)

    def GenTLI(self):
        # RF - if empty use calibre
        if self.rate_of_fire is None:
            RF = qjm_interps.RF_From_Calibre(self.calibre)
        else:
            RF = self.rate_of_fire * self.rf_multiple
        PTS = qjm_interps.PTS_From_Calibre(self.calibre)
        RIE = self.rie
        # RN
        RN_Range = 1 + (0.001 * self.range)**0.5
        RN_MV = 0.007 * self.muzzle_vel * (0.1 * self.calibre)**0.5
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
        MCE = 1
        AE = 1
        MBE = qjm_interps.MBE(self.barrels)
        self.RF = RF
        MRN = 1 - 0.19 * ((self.min_range - 100) / 100)
        PEN = 1 + 0.01 * signed_sqrt(self.penetration - 500)
        VEL = 1 + .001 * (self.muzzle_vel - 400)
        EN = self.enhancement
        self.TLI = RF * PTS * RIE * RN * A * RL * \
            SME * MCE * AE * MBE * MRN * PEN * VEL * EN
