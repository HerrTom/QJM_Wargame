import os

import wx
from wx.adv import DatePickerCtrl, TimePickerCtrl
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import wx.lib.newevent
from wx.lib.masked import TimeCtrl

import yaml

import equip_gui
import db_oob
import model_constants as mc

# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
# get the gamemaster folder
gmdir = os.path.abspath("../database/_gamemaster/")

#self.GetTopLevelParent().gdb = db_oob.oob_db()
side_dict = {"NATO": ["BRD","FRA","UK","USA"], "Warsaw Pact": ["USSR","DDR"]}

#checklist event
CheckList, EVT_CHECKLISTCTRL, = wx.lib.newevent.NewEvent()


def overmatch(oli,limit_oli,cap=100):
    # does the 1/2 factor overmatching
    if oli > limit_oli:
        overmatch_oli = oli - limit_oli
        new_oli = limit_oli + overmatch_oli/2
        if new_oli > cap*limit_oli:
            new_oli = cap*limit_oli
    else:
        new_oli = oli
    return new_oli

# class for checklist
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
    def OnCheckItem(self,index,flag):
        wx.PostEvent(self,CheckList(idx=index,flg=flag))

#class GamemasterFrame(wx.Frame):
class GamemasterWindow(wx.Panel):
    def __init__(self,parent):
        #wx.Frame.__init__(self,None,title="QJM Game Master")
        wx.Panel.__init__(self,parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((850,400))
        self.SetSize((800,600))
        
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(frame_sizer)
        # create a panel
        main_panel = wx.ScrolledWindow(self)
        frame_sizer.Add(main_panel,1,wx.ALL|wx.EXPAND)
        main_panel.SetScrollRate(0,5)
        #main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(side_sizer,1,wx.EXPAND|wx.ALL)
        main_panel.SetSizer(main_sizer)
        
        ### create a menu
        #menubar = wx.MenuBar()
        #filemenu = wx.Menu()
        #editmenu = wx.Menu()
        #reloadmenu = filemenu.Append(wx.ID_ANY,"&Load state")
        #filemenu.AppendSeparator()
        #quitmenu = filemenu.Append(wx.ID_EXIT, "&Quit", "Quit application")
        #dbmenu = editmenu.Append(wx.ID_ANY,"&Database Editor")
        #menubar.Append(filemenu,"&File")
        #menubar.Append(editmenu,"&Edit")
        #self.SetMenuBar(menubar)

        ## menu binds
        #self.Bind(wx.EVT_MENU,self.OnLoad,reloadmenu)
        #self.Bind(wx.EVT_MENU,self.OnClose,quitmenu)
        #self.Bind(wx.EVT_MENU,self.OnDbEdit,dbmenu)

        
        sides = ["","NATO","Warsaw Pact"]
        # attacker info
        attacker_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Attacker:")
        side_sizer.Add(attacker_sizer,1,wx.ALL|wx.EXPAND,5)
        # attacker side selecton
        self.attacker_side = wx.Choice(main_panel,-1,choices=sides)
        self.attacker_side.Bind(wx.EVT_CHOICE, self.OnAttackerSide)
        attacker_sizer.Add(self.attacker_side,0,wx.EXPAND,3)
        # attacker listctrl
        self.attacker_list = CheckListCtrl(main_panel)
        attacker_sizer.Add(self.attacker_list,1,wx.EXPAND,3)
        self.attacker_list.InsertColumn(0,"Formation",width=180)
        self.attacker_list.InsertColumn(1,"Strength")
        self.attacker_list.Bind(EVT_CHECKLISTCTRL,self.OnAttackerCheck)
        # TLI output
        self.oli_atk = 0 # tracker
        self.attacker_oli = wx.StaticText(main_panel,-1,"Total attacker OLI: {:>9,.0f}".format(0),)
        attacker_sizer.Add(self.attacker_oli,0,wx.CENTRE|wx.EXPAND|wx.ALL,3)
        
        # defender info
        defender_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Defender:")
        side_sizer.Add(defender_sizer,1,wx.ALL|wx.EXPAND,5)
        # defender side selecton
        self.defender_side = wx.Choice(main_panel,-1,choices=sides)
        self.defender_side.Bind(wx.EVT_CHOICE, self.OnDefenderSide)
        defender_sizer.Add(self.defender_side,0,wx.EXPAND,3)
        # defender listctrl
        self.defender_list = CheckListCtrl(main_panel)
        defender_sizer.Add(self.defender_list,1,wx.EXPAND,3)
        self.defender_list.InsertColumn(0,"Formation",width=180)
        self.defender_list.InsertColumn(1,"Strength")
        self.defender_list.Bind(EVT_CHECKLISTCTRL,self.OnDefenderCheck)
        # TLI output
        self.oli_def = 0 # tracker
        self.defender_oli = wx.StaticText(main_panel,-1,"Total defender OLI: {:>9,.0f}".format(0),)
        defender_sizer.Add(self.defender_oli,0,wx.CENTRE|wx.EXPAND|wx.ALL,3)
        
        # bind double click for SITREP
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.ShowSITREP,self.attacker_list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.ShowSITREP,self.defender_list)

        # battle data #########################
        data_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(data_sizer,0,wx.EXPAND|wx.ALL)
        # duration
        duration_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Duration (hrs):")
        self.duration = wx.SpinCtrl(main_panel,-1,min=4,max=48,initial=4)
        duration_sizer.Add(self.duration,1,wx.EXPAND|wx.ALL,3)
        data_sizer.Add(duration_sizer,0,wx.EXPAND|wx.ALL,5)
        # terrain
        terrain_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Terrain:")
        roughness = ["rugged, heavily wooded","rugged, mixed","rugged, bare",
                    "rolling, heavily wooded","rolling, mixed","rolling, bare",
                    "flat, heavily wooded","flat, mixed","flat, bare, hard",
                    "flat, desert","desert, sandy dunes","swamp, jungled","swamp, mixed or open",
                    "urban"]
        self.terrain = wx.Choice(main_panel,-1,choices=roughness)
        self.terrain.SetSelection(0)
        terrain_sizer.Add(self.terrain,1,wx.EXPAND|wx.ALL,3)
        data_sizer.Add(terrain_sizer,1,wx.EXPAND|wx.ALL,5)
        # weather
        weather_types = ["dry, sunshine, extreme heat", "dry, sunshine, temperate",
                        "dry, sunshine, extreme cold", "dry, overcast, extreme heat",
                        "dry, overcast, temperate", "dry, overcast, extreme cold", 
                        "wet, light, extreme heat", "wet, light, temperate", 
                        "wet, light, extreme cold", "wet, heavy, extreme heat", 
                        "wet, heavy, temperate", "wet, heavy, extreme cold",]
        weather_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Weather:")
        self.weather = wx.Choice(main_panel,-1,choices=weather_types)
        self.weather.SetSelection(0)
        weather_sizer.Add(self.weather,1,wx.EXPAND|wx.ALL,3)
        data_sizer.Add(weather_sizer,1,wx.EXPAND|wx.ALL,5)
        
        # 2nd row
        datar2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(datar2_sizer,0,wx.EXPAND|wx.ALL)
        # season
        season_sizer = wx.StaticBoxSizer(wx.HORIZONTAL,main_panel,"Season:")
        season_choices = ["winter, jungle","winter, desert","winter, temperate",
                        "spring, jungle","spring, desert","spring, temperate",
                        "summer, jungle","summer, desert","summer, temperate",
                        "fall, jungle","fall, desert","fall, temperate"]
        seasons_choices   = ["spring","summer","fall","winter"]
        seasonloc_choices = ["temperate","jungle","desert"]
        self.season = wx.Choice(main_panel,-1,choices=seasons_choices)
        self.seasonloc = wx.Choice(main_panel,-1,choices=seasonloc_choices)
        self.season.SetSelection(0)
        self.seasonloc.SetSelection(0)
        season_sizer.Add(self.season,1,wx.EXPAND|wx.ALL,3)
        season_sizer.Add(self.seasonloc,1,wx.EXPAND|wx.ALL,3)
        datar2_sizer.Add(season_sizer,1,wx.EXPAND|wx.ALL,5)
        # roads
        road_density_choices = ["dense network","medium network","sparse network"]
        road_quality_choices = ["good roads","mediocre roads","poor roads"]
        roads_sizer = wx.StaticBoxSizer(wx.HORIZONTAL,main_panel,"Roads:")
        self.road_density = wx.Choice(main_panel,-1,choices=road_density_choices)
        self.road_density.SetSelection(0)
        self.road_quality = wx.Choice(main_panel,-1,choices=road_quality_choices)
        self.road_quality.SetSelection(0)
        roads_sizer.Add(self.road_density,1,wx.EXPAND|wx.ALL,3)
        roads_sizer.Add(self.road_quality,1,wx.EXPAND|wx.ALL,3)
        datar2_sizer.Add(roads_sizer,1,wx.EXPAND|wx.ALL,5)
        # posture
        def_pos_choices = ["hasty","prepared","fortified", "delay","attack"]
        posture_sizer = wx.StaticBoxSizer(wx.VERTICAL,main_panel,"Defender posture:")
        self.posture = wx.Choice(main_panel,-1,choices=def_pos_choices)
        self.posture.SetSelection(0)
        posture_sizer.Add(self.posture,1,wx.EXPAND|wx.ALL,3)
        datar2_sizer.Add(posture_sizer,1,wx.EXPAND|wx.ALL,5)
        
        # date and name
        mdata_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(mdata_sizer,0,wx.EXPAND|wx.ALL,0)
        datesizer =  wx.StaticBoxSizer(wx.HORIZONTAL,main_panel,"Date and location:")
        self.date = DatePickerCtrl(main_panel,-1,style=wx.adv.DP_DROPDOWN)
        self.date.SetValue(wx.DateTime(1,10,1983)) # default is 1 Nov 1983
        #self.time = TimePickerCtrl(main_panel,-1)
        self.time = TimeCtrl(main_panel,-1,value='00:00',format='24HHMM')
        self.location = wx.TextCtrl(main_panel,-1,"")
        datesizer.Add(self.date,0,wx.EXPAND|wx.ALL,3)
        datesizer.Add(self.time,0,wx.EXPAND|wx.ALL,3)
        datesizer.Add(self.location,1,wx.EXPAND|wx.ALL,3)
        mdata_sizer.Add(datesizer,1,wx.EXPAND|wx.ALL,3)
        # river
        river_sizer = wx.StaticBoxSizer(wx.HORIZONTAL,main_panel,"River:")
        river_choices = ["no river","fordable, 20m","fordable, 50m","fordable, 100m","fordable, 500m",
                         "unfordable, 20m","unfordable, 50m","unfordable, 100m","unfordable, 500m",]
        self.river = wx.Choice(main_panel,-1,choices=river_choices)
        self.river.SetSelection(0)
        river_sizer.Add(self.river,1,wx.EXPAND|wx.ALL,3)
        mdata_sizer.Add(river_sizer,1,wx.EXPAND|wx.ALL,3)

        # frontage
        frontage_sizer = wx.StaticBoxSizer(wx.HORIZONTAL,main_panel,"Frontage:")
        self.frontage = wx.Slider(main_panel,-1,100,0,100,style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        frontage_sizer.Add(self.frontage,1,wx.EXPAND|wx.ALL,3)
        mdata_sizer.Add(frontage_sizer,1,wx.EXPAND|wx.ALL,3)


        # buttons
        button_panel = wx.Panel(self,style=wx.BORDER_THEME)
        frame_sizer.Add(button_panel,0,wx.ALL|wx.EXPAND)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_panel.SetSizer(button_sizer)
        #main_sizer.Add(button_sizer,0,wx.EXPAND|wx.ALL,)
        self.simulate_btn = wx.Button(button_panel,-1,"Simulate")
        self.simulate_btn.Bind(wx.EVT_BUTTON,self.OnSimulate)
        self.save_btn = wx.Button(button_panel,-1,"Save State")
        self.save_btn.Bind(wx.EVT_BUTTON,self.OnSave)
        self.load_btn = wx.Button(button_panel,-1,"Load State")
        self.load_btn.Bind(wx.EVT_BUTTON,self.OnLoad)
        button_sizer.Add(self.simulate_btn,1,wx.EXPAND|wx.ALL,3)
        button_sizer.Add(self.save_btn,1,wx.EXPAND|wx.ALL,3)
        button_sizer.Add(self.load_btn,1,wx.EXPAND|wx.ALL,3)
        
        
    def OnAttackerCheck(self,event):
        idx = event.idx
        name = self.attacker_list.GetItemText(idx,col=0)
        form = self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(name)
        flag = event.flg
        if flag: # if checked, add the OLI value
            self.oli_atk += form.OLI
        else: # if unchecked, remove it
            self.oli_atk += -form.OLI
        # update the OLI display
        self.attacker_oli.SetLabel("Total attacker OLI: {:>9,.0f}".format(self.oli_atk))
        
    def OnDefenderCheck(self,event):
        idx = event.idx
        name = self.defender_list.GetItemText(idx,col=0)
        form = self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(name)
        flag = event.flg
        if flag: # if checked, add the OLI value
            self.oli_def += form.OLI
        else: # if unchecked, remove it
            self.oli_def += -form.OLI
        # update the OLI display
        self.defender_oli.SetLabel("Total defender OLI: {:>9,.0f}".format(self.oli_def))
    
    def OnAttackerSide(self,event):
        # set both OLI values to zero
        self.attacker_oli.SetLabel("Total attacker OLI: {:>9,.0f}".format(0))
        self.defender_oli.SetLabel("Total defender OLI: {:>9,.0f}".format(0))
        self.attacker_list.DeleteAllItems() # clear items
        side = self.attacker_side.GetString(self.attacker_side.GetSelection())
        if side == "":
            return
        faction_search = side_dict[side]
        formations = self.GetTopLevelParent().gdb.gm_forms_db.forms
        for form in formations:
            if form.faction in faction_search:
                entry = [form.name, "{:,.0f}".format(form.OLI)]
                self.attacker_list.Append(entry)
                
    def OnDefenderSide(self,event):
        self.defender_list.DeleteAllItems() # clear items
        side = self.defender_side.GetString(self.defender_side.GetSelection())
        if side == "":
            return
        faction_search = side_dict[side]
        formations = self.GetTopLevelParent().gdb.gm_forms_db.forms
        for form in formations:
            if form.faction in faction_search:
                entry = [form.name, "{:,.0f}".format(form.OLI)]
                self.defender_list.Append(entry)
    
    def OnSimulate(self,event):
        # Multiply force strength by operational variables - overall forms a big ugly equation
        # force strength is shown by:
        # S = [(ws+Wmg+Whw)*rn]+(wgi*rn)+[(Wg+Wgy)*(rwg*hwg*zwg*wyg)]+(Wi*rwi*hwi)+ ...
        #        ...(Wy*rwy*hwy*zyw*wyy) + Wgi + Wgy
        #   note Wgi is included up to enemy armour OLI, then only half excess is added
        #   same applies for Wfgy for air defense weapons, up to hostile Close Air Support (Wey)
        # Air firepower (Wy) over sum of all ground firepower is not fully effective
        # Wy > Ws + Wmy + Whw + Wgi + Wg + Wgy + Wi, only half of excess Wy is applied
        #       maximum Wy is 3x ground weapons firepower
        #
        # operational factors are given by:
        # [Ma-(1-rm*hm)(Ma-1)]*le*t*o*b*us*ru*hu*zu*v
        #       where v = 1-(N*uv/ru*(Se/Sf)**.5 * vy*vr)/Sf
        # Following are degredation factors
        # le: leadership - typically 1
        # t: training/experience - typically 1
        # o: morale - typically 1
        # b: logistical capability - typically 1
        
        # Get OLI values from checked attackers
        attackers = list()
        attackers_forms = list()
        for idx in range(self.attacker_list.GetItemCount()):
            if self.attacker_list.IsChecked(idx):
                attackers.append(self.attacker_list.GetItemText(idx))
        for form in attackers:
            attackers_forms.append(self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(form))
        attacker_oli = self.GetTopLevelParent().gdb.gm_forms_db.oli_by_names(attackers)
        N_attacker = self.GetTopLevelParent().gdb.gm_forms_db.pers_by_names(attackers)
        J_attacker = self.GetTopLevelParent().gdb.gm_forms_db.vehicles_by_names(attackers,self.GetTopLevelParent().gdb.equip_db)
        
        # Get OLI values from checked defenders
        defenders = list()
        defenders_forms = list()
        for idx in range(self.defender_list.GetItemCount()):
            if self.defender_list.IsChecked(idx):
                defenders.append(self.defender_list.GetItemText(idx))
        defender_oli = self.GetTopLevelParent().gdb.gm_forms_db.oli_by_names(defenders)
        for form in defenders:
            defenders_forms.append(self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(form))
        
        N_defender = self.GetTopLevelParent().gdb.gm_forms_db.pers_by_names(defenders)
        J_defender = self.GetTopLevelParent().gdb.gm_forms_db.vehicles_by_names(defenders,self.GetTopLevelParent().gdb.equip_db)
        
        # get environment data from the forms
        terrain         = self.terrain.GetString(self.terrain.GetSelection())
        weather         = self.weather.GetString(self.weather.GetSelection())
        season_sel      = self.season.GetString(self.season.GetSelection())
        season_locale   = self.seasonloc.GetString(self.seasonloc.GetSelection())
        river           = self.river.GetString(self.river.GetSelection())
        time_day        = self.time.GetValue()
        print(time_day)
        # determine if it is day or night
        if time_day > "06:00" and time_day < "20:00":
            daytime = True
        else:
            daytime = False


        # get the frontage of the attack (% of defenders)
        frontage = self.frontage.GetValue() / 100

        seasonstr = season_sel+', '+season_locale
        #print(seasonstr)

        # get the posture from the form
        def_posture = self.posture.GetString(self.posture.GetSelection())
        
        # Terrain effectiveness values (r) and weather effectiveness (h)
        # infantry & antitank
        rn = mc.terrain(terrain,'inf')
        # artillery & air defence
        rwg = mc.terrain(terrain,'arty')
        hwg = mc.weather(weather,'arty')
        zwg = mc.season(seasonstr,'arty')
        # tanks
        rwi = mc.terrain(terrain,'tank')
        hwi = mc.weather(weather,'tank')
        # aircraft
        rwy = mc.terrain(terrain,'air')
        hwy = mc.weather(weather,'air')
        zwy = mc.season(seasonstr,'air')
        
        # these constants are for air superiority
        wyg = 1
        wyy = 1
        
        print(attacker_oli.air, attacker_oli.ad)
        print(defender_oli.air, defender_oli.ad)

        # attacker data:
        Wain = attacker_oli.inf
        Waat = attacker_oli.at
        Watn = attacker_oli.afv
        Waar = attacker_oli.arty
        Waad = attacker_oli.ad
        Waai = attacker_oli.air 
        
        # defender data
        Wdin = defender_oli.inf
        Wdat = defender_oli.at
        Wdtn = defender_oli.afv
        Wdar = defender_oli.arty
        Wdad = defender_oli.ad
        Wdai = defender_oli.air 
        
        # deal with overmatches in at and ad OLIs
        Waat = overmatch(Waat,Wdtn)
        Wdat = overmatch(Wdat,Watn)
        Waad = overmatch(Waad,Wdai,cap=3)
        Wdad = overmatch(Wdad,Waai,cap=3)
        
        # using my "simplified" formula
        S_attacker = ((Wain + Waat)*rn + (Waar+Waad*wyg)*rwg*hwg*zwg + 
                            Watn*rwi*hwi + Waai*rwy*hwy*zwy*wyy)
        S_defender = ((Wdin + Wdat)*rn + (Wdar+Wdad*wyg)*rwg*hwg*zwg + 
                            Wdtn*rwi*hwi + Wdai*rwy*hwy*zwy*wyy) * frontage
        
        
        # get the combat power
        Faj = 1 # judgement degrading factor for attacker
        Fdj = 1 # judgement degrading factor for defender
        uas = mc.stren_posture_factor('attack') # posture for attacker
        uds = mc.stren_posture_factor(def_posture) # posture for defender
        rau = 1 # terrain for attacker - attacker is always 1
        rdu = mc.terrain(terrain,'defpos') # terrain for defender - uses terrain defpos
        hau = mc.weather(weather,'attack') # weather for attacker
        hdu = 1 # weather for defender - defender is always 1
        zau = mc.season(seasonstr,'attack') # season for attacker
        zdu = 1 # season for defender - defender is always 1
        
        # mobility factors
        road_quality = self.road_quality.GetString(self.road_quality.GetSelection())
        road_density = self.road_density.GetString(self.road_density.GetSelection())
        rma = mc.terrain(terrain,'mobility')
        hma = mc.weather(weather,'mobility')
        mya = 1 # don't know what this factor is
        myd = 1 # don't know what this factor is either
        
        
        # vulnerability factors
        uav = mc.vuln_posture_factor('attack')
        udv = mc.vuln_posture_factor(def_posture)
        vay = 1 # air superiority vulnerability
        vdy = 1 # air superiority vulnerability
        var = 1 # shoreline vulnerability
        vdr = 1 # shoreline vulnerability
        
        # mobility
        MFactor = 12 # 20 for WWII
        M_attacker = (((N_attacker + MFactor * J_attacker + Waar) * mya / N_attacker) /
                        ((N_defender + MFactor*J_defender + Wdar) * myd / N_defender))**0.5
        M_defender = 1 # always 1
        
        ma_operational = M_attacker - (1-rma*hma)*(M_attacker-1)
        md_operational = M_defender
        
        # vulnerability
        Vuln_attacker = N_attacker * uav / rau * (S_defender/S_attacker)**0.5 * vay * var
        print("Vulnerability calcs:",N_attacker,uav,rau,S_defender,S_attacker,vay,var)
        Vuln_defender = N_defender * udv / rdu * (S_attacker/S_defender)**0.5 * vdy * vdr
        va_operational = (1-Vuln_attacker/S_attacker)
        vd_operational = (1-Vuln_defender/S_defender)
        
        if va_operational > 0.8:
            va_operational = 0.8
        elif va_operational > 0.3:
            va_operational = 0.3 + 0.1 * (va_operational-0.3)
        else:
            va_operational = 0.3
        if vd_operational > 0.8:
            vd_operational = 0.8
        elif vd_operational > 0.3:
            vd_operational = 0.3 + 0.1 * (vd_operational-0.3)
        else:
            vd_operational = 0.3
        
        # note that the CEV is already contained in the OLI output
        Op_attacker = Faj * uas*rau*hau*zau
        Op_defender = Fdj * uds*rdu*hdu*zdu
        
        P_attacker = S_attacker * ma_operational * Op_attacker * va_operational
        P_defender = S_defender * md_operational * Op_defender * vd_operational
        P_ratio = P_attacker / P_defender
        
        dateval = self.date.GetValue().FormatISODate()
        #timeval = self.time.GetValue().FormatISOTime()
        timeval = self.time.GetWxDateTime().FormatISOTime()
        location = self.location.GetValue()
        
        print("*** START REPORT ***\n")
        
        print("{} engages {}\n".format(attackers, defenders))
        
        print("Base OLI data: (W) || Attacker: {:9,.0f} | Defender: {:9,.0f} | Ratio {:.1f}".format(
                attacker_oli.total,defender_oli.total,attacker_oli.total/defender_oli.total))
                
        print("Strength data (S): || Attacker: {:9,.0f} | Defender: {:9,.0f} | Ratio {:.1f}".format(
                S_attacker,S_defender,S_attacker/S_defender))
        
        print("Combat Power (P):  || Attacker: {:9,.0f} | Defender: {:9,.0f} | Ratio {:.1f}".format(
                P_attacker,P_defender,P_attacker/P_defender))
        
        print("\n Key factors: |  Attacker | Defender\n",
              "Strength     | {:9,.0f} | {:9,.0f}\n".format(S_attacker,S_defender),
              "Mobility     | {:9,.2f} | {:9,.2f}\n".format(M_attacker,M_defender),
              "Vulnerability| {:9,.0f} | {:9,.0f}\n".format(Vuln_attacker,Vuln_defender),
              "Op. Vuln     | {:9,.3f} | {:9,.3f}\n".format(va_operational,vd_operational),)
        
        # advance rate - probably need to run for each individual formation?
        for name in attackers:
            index = self.GetTopLevelParent().gdb.gm_forms_db.names.index(name)
            unittype = self.GetTopLevelParent().gdb.gm_forms_db.forms[index].type
            adv_base = mc.advance_rate_base(P_ratio,unittype,def_posture)
            adv_roads = mc.advance_rate_road(road_quality,road_density)
            adv_terr = mc.advance_rate_terr(terrain,unittype)
            adv_river = mc.river_obstacle_factor(river)
            adv_rate = adv_base * adv_roads * adv_terr * adv_river
            atk_losses = self.GetTopLevelParent().gdb.gm_forms_db.forms[index].casualties(P_ratio,'attack',day=daytime,
                                            duration=self.duration.GetValue(),pers=N_attacker)
            print("{} advance rate: {:.1f} km/day".format(self.GetTopLevelParent().gdb.gm_forms_db.forms[index].name,adv_rate))
            print("---")
            print(self.GetTopLevelParent().gdb.gm_forms_db.forms[index].SITREP(atk_losses,activity='Attacking',datestr="{} {}".format(dateval,timeval),location=location,writefolder=gmdir+"\\reports"))
        
        for name in defenders:
            index = self.GetTopLevelParent().gdb.gm_forms_db.names.index(name)
            def_losses = self.GetTopLevelParent().gdb.gm_forms_db.forms[index].casualties(P_ratio,def_posture,day=daytime,
                                            duration=self.duration.GetValue(),exposure=frontage,pers=N_defender)
            print("---")
            print(self.GetTopLevelParent().gdb.gm_forms_db.forms[index].SITREP(def_losses,activity=def_posture+' defense',datestr="{} {}".format(dateval,timeval),location=location,writefolder=gmdir+"\\reports"))
        
        # finish the report
        print("*** END REPORT ***")
    
    def ShowSITREP(self,event):
        # get the list that was clicked
        formlist = event.GetEventObject()
        # get the item from the list
        item = formlist.GetItemText(event.GetIndex(),col=0)
        # print a sitrep for the item
        form = self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(item)
        infoframe = formation_info_form(self,form.SITREP(activity='None')+
                                        "\nNo TLI data for:\n{}".format(form.NoTLIData),item)
        infoframe.Show()

    def OnDbEdit(self,event):
        eqp = equip_gui.equipment_gui_frame()
        eqp.Show()

    def OnSave(self,event):
        dlg = wx.DirDialog(self,message="Master folder for formations to save",
                           defaultPath=gmdir)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            for form in self.GetTopLevelParent().gdb.gm_forms_db.forms:
                form.output(path)
    
    def OnLoad(self,event):
        dlg = wx.DirDialog(self,message="Master folder for formations to load",
                           defaultPath=gmdir)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.GetTopLevelParent().gdb.load_gm_formations(path)
    
    def OnClose(self,event):
        dlg = wx.MessageDialog(self, 
            "Are you sure you want to close?",
            "Confirm exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

class formation_info_form(wx.Frame):
     def __init__(self,parent,information,title="Information"):
        wx.Frame.__init__(self,parent,title=title,
                            style = wx.DEFAULT_FRAME_STYLE)
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.info_box = wx.TextCtrl(panel,-1,information,style = wx.TE_MULTILINE)
        main_sizer.Add(self.info_box,1,wx.EXPAND|wx.ALL,5)
        
        panel.SetSizerAndFit(main_sizer)
        #self.Fit()
