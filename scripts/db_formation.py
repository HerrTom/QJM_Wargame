from collections import Counter
# future work I want to do here is to combine the formation_group and 
# formation objects such that any formation can have sub-formations

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
    
    def GetOLI(self,):
        return ("OLI statistics for {}\n"
        "Overall:     {:,.0f}\n"
        "Infantry:    {:,.0f}\n"
        "AFVs:        {:,.0f}\n"
        "Anti-tank:   {:,.0f}\n"
        "Artillery:   {:,.0f}\n"
        "Air defense: {:,.0f}\n"
        "No TLI for: {}\n").format(self.name,self.OLI,self.OLI_inf,self.OLI_afv,self.OLI_at,
                                        self.OLI_arty,self.OLI_ad,
                                        ListToFormattedString(self.NoTLIData))
    
    def GenOLI(self, equipment_list):
        self.OLI        = 0
        self.OLI_inf    = 0 # infantry
        self.OLI_afv    = 0 # tanks
        self.OLI_at     = 0 # anti tank
        self.OLI_arty   = 0 # artillery
        self.OLI_ad     = 0 # air defense
        
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
            formation = self.formation_by_name(name)
            CEV = formation.CEV
            OLI.total += formation.OLI
            OLI.inf += formation.OLI_inf
            OLI.afv += formation.OLI_afv
            OLI.at += formation.OLI_at
            OLI.arty += formation.OLI_arty
            OLI.ad += formation.OLI_ad
        return OLI
    
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