from scipy.interpolate import interp1d

# constants dictionaries/functions

def terrain(terraintype,factor):
    # factors are:
    # mobility, defpos, inf, arty, air, tanks
    factor_ls = ['mobility','defpos','inf','arty','air','tank']
    idx = factor_ls.index(factor) # gets the index to return from dictionary
    
    terrdict = {"rugged, heavily wooded": [0.4, 1.5, 0.6, 0.7, 0.8, 0.2],
                "rugged, mixed": [0.5, 1.55, 0.7, 0.8, 0.9, 0.4],
                "rugged, bare": [0.6, 1.45, 0.8, 0.9, 0.95, 0.5],
                "rolling, heavily wooded": [0.6, 1.35, 0.8, 0.8, 0.9, 0.8],
                "rolling, mixed": [0.8, 1.3, 0.9, 0.9, 0.95, 0.8],
                "rolling, bare": [1, 1.2, 1, 1, 1, 1],
                "flat, heavily wooded": [0.7, 1.2, 0.8, 0.9, 0.9, 0.7],
                "flat, mixed": [0.9, 1.2, 0.9, 1, 0.95, 0.9],
                "flat, bare, hard": [1.05, 1.05, 1, 1, 1, 1],
                "flat, desert": [0.95, 1.18, 1, 1, 1, 1],
                "desert, sandy dunes": [0.3, 1.4, 0.6, 0.8, 0.8, 0.2],
                "swamp, jungled": [0.3, 1.4, 0.6, 0.8, 0.8, 0.2],
                "swamp mixed or open": [0.4, 1.3, 0.8, 0.9, 0.95, 0.3],
                "urban": [0.7, 1.4, 0.8, 0.9, 0.9, 0.7]}
    return terrdict[terraintype][idx]
    
    
    
def weather(weathertype,factor):
    # factors are:
    # mobility, defpos, inf, arty, air, tanks
    factor_ls = ['mobility','attack','arty','air','tank']
    idx = factor_ls.index(factor) # gets the index to return from dictionary    
    weatherdict = {"dry, sunshine, extreme heat":      [0.9,1,1,1,0.9],
                    "dry, sunshine, temperate":         [1,1,1,1,1],
                    "dry, sunshine, extreme cold":      [0.9,0.9,0.9,1,0.9],
                    "dry, overcast, extreme heat":      [1,1,1,0.7,1],
                    "dry, overcast, temperate":         [1,1,1,0.7,1],
                    "dry, overcast, extreme cold":      [0.9,0.9,0.9,0.7,0.8],
                    "wet, light, extreme heat":         [0.9,0.9,0.9,0.5,0.7],
                    "wet, light, temperate":            [0.8,0.9,1,0.5,0.7],
                    "wet, light, extreme cold":         [0.8,0.9,1,0.5,0.7],
                    "wet, heavy, extreme heat":         [0.5,0.6,0.9,0.2,0.6],
                    "wet, heavy, temperate":            [0.6,0.7,0.9,0.2,0.5],
                    "wet, heavy, extreme cold":         [0.5,0.6,0.8,0.2,0.5]}
    return weatherdict[weathertype][idx]
    
def season(seasontype,factor):
    factor_ls = ['attack','arty','air']
    idx = factor_ls.index(factor)
    seasondict = {"winter, jungle": [1.1,0.9,0.7],
                    "winter, desert": [1,1,1],
                    "winter, temperate": [1,1,1],
                    "spring, jungle": [1.1,0.9,0.7],
                    "spring, desert": [1,1,1],
                    "spring, temperate": [1.1,1,0.9],
                    "summer, jungle": [1.1,0.9,0.7],
                    "summer, desert": [1,1,1],
                    "summer, temperate": [1.1,0.9,1],
                    "fall, jungle": [1.1,0.9,0.7],
                    "fall, desert": [1,1,1],
                    "fall, temperate": [1.1,1,0.9],}
    return seasondict[seasontype][idx]
    
def advance_rate_base(ratio,unittype,deftype):
    pratio_pts = [1, 1.1, 1.25, 1.45, 1.75, 2.25, 3.0, 4.25, 6.0]
    advance = {
    "arm": {"hasty": [4,5,6,9,12,16,20,40,60],
            "prepared": [2,2.25,2.5,4,6,8,10,20,30],
            "fortified": [1,1.85,1.5,2,3,4,5,10,30],},
    "mech": {"hasty": [4,4.5,5,7.5,10,13,16,30,48],
            "prepared": [2,2.25,2.8,3.5,5,7,8,16,24],
            "fortified": [1,1.85,1.5,2,2.5,3,4,8,24],},
    "inf": {"hasty": [4,4.5,5,6.5,8,10,12,18,24],
            "prepared": [2,2.25,2.5,3,4,5,6,10,12],
            "fortified": [1,1.85,1.5,1.75,2,2.5,3,6,12],},
    }
    if ratio < 1:
        base = 0
    #elif ratio < max(pratio_pts):
    else:
        rate_pts = advance[unittype][deftype]
        rate_interp = interp1d(pratio_pts,rate_pts,'cubic',fill_value='extrapolate')
        base = float(rate_interp(ratio))
    #else:
    #    base = 60
    return base

def advance_rate_terr(terr,unittype):
    advance = {"rugged, heavily wooded": [0.4, 0.2],
               "rugged, mixed": [0.5, 0.4],
               "rugged, bare": [0.6, 0.5],
               "rolling, heavily wooded": [0.6, 0.6],
               "rolling, mixed": [0.8, 0.8],
               "rolling, bare": [1, 1],
               "flat, heavily wooded": [0.7, 0.7],
               "flat, mixed": [0.9, 0.9],
               "flat, bare, hard": [1.05, 1],
               "flat, desert": [0.95, 1],
               "desert, sandy dunes": [0.3, 0.6],
               "swamp, jungled": [0.3, 0.2],
               "swamp mixed or open":  [0.4, 0.3],
               "urban": [0.7, 0.7],}
    adv_terr = advance[terr]
    if unittype == 'arm':
        return adv_terr[1]
    else:
        return adv_terr[0]

def advance_rate_road(quality,density):
    qual_dict = {"good roads": 1.0, "mediocre roads": 0.8, "poor roads": 0.6}
    dens_dict = {"dense network": 1.0, "medium network": 0.8, "sparse network": 0.6}
    return qual_dict[quality]*dens_dict[density]
    
    
    
def vuln_posture_factor(posture):
    pos_dict = {"attack": 1.0,
                "hasty": 0.7,
                "prepared": 0.6,
                "fortified": 0.5,
                "withdrawal": 0.85,
                "delay": 0.65}
    return pos_dict[posture]

def stren_posture_factor(posture):
    pos_dict = {"attack": 1.0,
                "hasty": 1.3,
                "prepared": 1.5,
                "fortified": 1.6,
                "withdrawal": 1.15,
                "delay": 1.2}
    return pos_dict[posture]
    
    