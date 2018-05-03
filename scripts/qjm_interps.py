from scipy.interpolate import pchip_interpolate, interp1d
from numpy import loadtxt

def PTS_From_Calibre(calibre):
    InterpCalibre = [
        0,
        5,
        5.45,
        10,
        12.7,
        14.7,
        20,
        30,
        40,
        60,
        75,
        81,
        90,
        105,
        120,
        130,
        155,
        175,
        203,
        225,
        250,
        275,
        300,
        325,
        350,
        375,
        400,
        450,
        500,
        550,
        600,
        650,
        700,
        800,
        900,
        1000]
    InterpPTS = [
        1,
        1,
        1,
        1,
        2,
        2,
        40,
        100,
        170,
        344,
        625,
        752,
        985,
        1485,
        2002,
        2437,
        3594,
        4375,
        5000,
        5560,
        6125,
        6570,
        6985,
        7250,
        7500,
        7810,
        8000,
        8560,
        9000,
        9400,
        9680,
        9938,
        10187,
        10500,
        10750,
        10900]
    interp = interp1d(InterpCalibre, InterpPTS)
    # return int(pchip_interpolate(InterpCalibre,InterpPTS,calibre))
    return int(interp(calibre))


def RF_From_Calibre(calibre):
    InterpCalibre = [
        20,
        30,
        40,
        60,
        75,
        81,
        90,
        105,
        120,
        130,
        155,
        175,
        203,
        225,
        250,
        275,
        300,
        325,
        350,
        375,
        400,
        450,
        500,
        550,
        600,
        650,
        700,
        800,
        900,
        1000]
    InterpRF = [
        295,
        260,
        225,
        175,
        152,
        144,
        134,
        113,
        99,
        90,
        60,
        47,
        30,
        25,
        22,
        18,
        16,
        15,
        13,
        12,
        10,
        8,
        7,
        5,
        3,
        2,
        2,
        2,
        2,
        2]
    return int(pchip_interpolate(InterpCalibre, InterpRF, calibre))


def MBE(barrels):
    MBEDict = { 1: 1,
                2: 1.5,
                3: 1.83,
                4: 2.08,
                5: 2.28,
                6: 2.47,
                7: 2.65,
                8: 2.82,
                9: 2.98,
                10: 3.13,
                11: 3.27,
                12: 3.4,
                13: 3.52,
                14: 3.63,
                15: 3.73,
                16: 3.82,
                17: 3.9,
                18: 3.97,
                19: 4.03,
                20: 4.08,
                21: 4.12,
                22: 4.15,
                23: 4.17,
                24: 4.18}
    if barrels < 25:
        return MBEDict[barrels]
    else:
        return 4.18


def Calibre_From_Weight(weight):
    data = loadtxt("../database/lookup_tables/weight_calibre.csv",delimiter=',',
            skiprows=1)
    weight_pts = data[:,0]
    calibre_pts = data[:,1]
    calibre_interp = interp1d(weight_pts,calibre_pts,'slinear',fill_value='extrapolate')
    return calibre_interp(weight)


def ASE(AmmoRatio):
    InterpAmmo = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1, 100]
    InterpASE = [0, 0.2, 0.5, 0.75, 0.85, 0.9, 0.95, 1, 1]
    interp = interp1d(InterpAmmo, InterpASE)
    return interp(AmmoRatio)

def casualty_size_factor(personnel): # data from TNDM
    data = loadtxt("../database/lookup_tables/strength_size_factor.csv",delimiter=',',
            skiprows=1)
    pers_pts = data[:,0]
    factor_pts = data[:,1]
    pers_factor_interp = interp1d(pers_pts,factor_pts,'slinear',fill_value='extrapolate')
    return pers_factor_interp(personnel)

def casualty_opposition_factor(power_ratio):
    data = loadtxt("../database/lookup_tables/opposition_factor.csv",delimiter=',',
            skiprows=1)
    power_pts = data[:,0]
    factor_pts = data[:,1]
    casualty_op_interp = interp1d(power_pts,factor_pts,'slinear',fill_value='extrapolate')
    return casualty_op_interp(power_ratio)
