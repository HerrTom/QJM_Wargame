import wx
import os
import yaml
from fuzzywuzzy import process

import db_oob
import db_formation
import db_weapons
import db_equipment

import weapon_gui

# GUI script for creating database entries


# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# global database
global gdb
gdb = db_oob.oob_db()

weap_list_rows = 6

class MatchingCombo(wx.ComboBox):
    def __init__(self,*args, **kwargs):
        # init the combo box
        wx.ComboBox.__init__(self,*args,**kwargs)
        # as long as 
        self.Bind(wx.EVT_KILL_FOCUS,self.CheckItems)
        
    def CheckItems(self,event):
        entered_text = self.GetValue()
        if entered_text != "": # only check if we have actually entered something
            # get through the items
            options = list()
            for i in range(self.GetCount()):
                options.append(self.GetString(i))
            
            # search for the closest match
            match = process.extractOne(entered_text,options)
            self.SetValue(match[0])
        pass
        

# Equipment editor frame
class equipment_gui_frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title="QJM Equipment Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # create a menu bar on the top
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        
        # submenu for New
        toolsmenu = wx.Menu()
        weaponmenu = toolsmenu.Append(wx.ID_ANY,"&Weapon Editor","Edit weapon entries")
        self.Bind(wx.EVT_MENU,self.on_new_weap,weaponmenu)
        
        # File menu appends
        infomenu = filemenu.Append(wx.ID_ANY,"&Display formation info")
        reloadmenu = filemenu.Append(wx.ID_ANY,"&Reload database")
        filemenu.AppendSeparator()
        quitmenu = filemenu.Append(wx.ID_EXIT, "&Quit", "Quit application")
        self.Bind(wx.EVT_MENU,self.OnClose,quitmenu)
        self.Bind(wx.EVT_MENU,self.show_info,infomenu)
        self.Bind(wx.EVT_MENU,self.on_reload_db,reloadmenu)
        menubar.Append(filemenu, "&File")
        menubar.Append(toolsmenu, "&Tools")

        self.SetMenuBar(menubar)
        
        
        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # panel on the left will have the ListBox and new/copy/save buttons
        left_panel = wx.Panel(self,)
        lp_sizer = wx.BoxSizer(wx.VERTICAL)
        lp_staticsizer = wx.StaticBoxSizer(wx.VERTICAL,left_panel,"Equipment:")
        lp_sizer.Add(lp_staticsizer, 1, wx.ALL, 3)

        # equipment list
        self.equip_listbox = wx.ListBox(left_panel,-1, choices=gdb.equip_db.names,
                                        style=wx.LB_ALWAYS_SB,size=(180,-1))
        lp_staticsizer.Add(self.equip_listbox, 1, wx.ALL|wx.EXPAND, 3)
        
        self.equip_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_equipment)
        
        # OLI value
        self.OLIDisplay = wx.StaticText(left_panel,-1,"OLI: {:>5,.0f}".format(0))
        lp_sizer.Add(self.OLIDisplay,0,wx.CENTER,5)
        
        # buttons
        self.new_button = wx.Button(left_panel, -1,"New",)
        self.save_button = wx.Button(left_panel, -1,"Save",)
        
        self.new_button.Bind(wx.EVT_BUTTON, self.clear_form)
        self.save_button.Bind(wx.EVT_BUTTON, self.save_equipment)
        
        lp_sizer.Add(self.new_button,  0, wx.ALL|wx.EXPAND, 3)
        lp_sizer.Add(self.save_button, 0, wx.ALL|wx.EXPAND, 3)
        
        
        # right hand panel has all the data for the entry
        self.right_panel = wx.ScrolledWindow(self)
        rp_sizer = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Equipment Entry:")
        # set up the scroll bar
        self.right_panel.SetScrollRate(0,5)
        
        # equip name entry
        self.equip_name = wx.TextCtrl(self.right_panel,-1,'')
        equip_name_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Name:")
        equip_name_static.Add(self.equip_name,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(equip_name_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # bind the event handler that will search for existing names and highlight if a hit
        self.equip_name.Bind(wx.EVT_TEXT, self.on_name_box)
        
        # equip name entry
        self.nation = wx.TextCtrl(self.right_panel,-1,'')
        nation_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Nationality/Folder:")
        nation_static.Add(self.nation,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(nation_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # equip type choice box
        # equip type defines the data entry values
        equip_type_choices = ["Infantry", "APC", "IFV", "AFV","AT","SP AT",
                                "Artillery","SP Artillery","AD","SP AD"] # defines available choices
        self.equip_type = wx.Choice(self.right_panel,-1,choices=equip_type_choices,)
        equip_type_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Equipment type:")
        equip_type_static.Add(self.equip_type,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(equip_type_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        self.equip_type.Bind(wx.EVT_CHOICE,self.disable_by_type)
        
        # weapons list
        self.weaps_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Weapons:")
        rp_sizer.Add(self.weaps_static,0,wx.ALL|wx.EXPAND,5)
        #self.weaps_subsizer = wx.BoxSizer(wx.VERTICAL)
        #self.weaps_static.Add(self.weaps_subsizer,0,wx.ALL|wx.EXPAND,0)
        self.weapons_list(weap_list_rows)
        
        # operational range
        self.op_range = wx.TextCtrl(self.right_panel,-1,'')
        op_range_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Operational range (km):")
        op_range_static.Add(self.op_range,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(op_range_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # weight
        self.weight = wx.TextCtrl(self.right_panel,-1,'')
        weight_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Weight (t):")
        weight_static.Add(self.weight,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weight_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)  
        
        # speed
        self.speed = wx.TextCtrl(self.right_panel,-1,'')
        speed_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Road speed (km/h):")
        speed_static.Add(self.speed,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(speed_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # primary ammo store
        self.ammo_store = wx.TextCtrl(self.right_panel,-1,'')
        ammo_store_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Primary ammo store:")
        ammo_store_static.Add(self.ammo_store,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(ammo_store_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # crew
        self.crew = wx.TextCtrl(self.right_panel,-1,'')
        crew_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Crew:")
        crew_static.Add(self.crew,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(crew_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # armour
        armour_choices = ["aluminium","steel","early composite","composite",
                            "reactive","modern reactive",]
        armour_static = wx.StaticBoxSizer(wx.HORIZONTAL,self.right_panel,"Armour type:")
        self.armour = wx.Choice(self.right_panel,-1,choices=armour_choices)
        armour_static.Add(self.armour,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(armour_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # fire control
        FCE_choices = ["none", "steroscopic rangefinder", "laser rangefinder", 
                        "early thermal optics", "thermal optics",]
        FCE_static = wx.StaticBoxSizer(wx.HORIZONTAL,self.right_panel,"FCE type:")
        self.FCE = wx.Choice(self.right_panel,-1,choices=FCE_choices)
        FCE_static.Add(self.FCE,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(FCE_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # PC squad
        squad_static = wx.StaticBoxSizer(wx.HORIZONTAL,self.right_panel,"Mounted squad OLI:")
        self.squad = wx.TextCtrl(self.right_panel,-1,"")
        self.squad_btn = wx.Button(self.right_panel,-1,"Calc")
        self.squad_btn.Bind(wx.EVT_BUTTON, self.on_squad_btn)
        squad_static.Add(self.squad,1,wx.ALL|wx.EXPAND,3)
        squad_static.Add(self.squad_btn,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(squad_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # Amphibious
        misc_static = wx.StaticBoxSizer(wx.HORIZONTAL,self.right_panel,"Other options:")
        self.amph = wx.CheckBox(self.right_panel,-1,"Amphibious")
        misc_static.Add(self.amph,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(misc_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # disable everything by default
        self.disable_all()
        
        # wrap up the gui
        left_panel.SetSizer(lp_sizer)
        self.right_panel.SetSizer(rp_sizer)
        frame_sizer.Add(left_panel, 0, wx.EXPAND)
        frame_sizer.Add(self.right_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)
        self.SetSize((400,500))
        
    
    # GUI generation functions
    def disable_all(self):
        # function to disable all elements
        self.op_range.Enable(False)
        self.weight.Enable(False)
        self.speed.Enable(False)
        self.ammo_store.Enable(False)
        self.crew.Enable(False)
        self.armour.Enable(False)
        self.FCE.Enable(False)
        self.squad.Enable(False)
        self.amph.Enable(False)
        # reset the FCE choices
        FCE_choices = ["none", "steroscopic rangefinder", "laser rangefinder", 
                        "early thermal optics", "thermal optics",]
        self.FCE.Set(FCE_choices)
        
    def disable_by_type(self,event):
        # disables entries based on the combo box selection
        self.disable_all()
        # enable based on entity
        type = self.equip_type.GetString(self.equip_type.GetSelection())
        if type == "AFV":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.FCE.Enable(True)
            self.amph.Enable(True)
        elif type == "IFV":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.FCE.Enable(True)
            self.squad.Enable(True)
            self.amph.Enable(True)
        elif type == "APC":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.squad.Enable(True)
            self.amph.Enable(True)
        if type == "SP AT":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.amph.Enable(True)
        if type == "SP Artillery":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.amph.Enable(True)
        if type == "SP AD":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.FCE.Enable(True)
            self.amph.Enable(True)
            FCE_choices = ["none", "optical", "small radar","medium radar","large radar"]
            self.FCE.Set(FCE_choices)
        else: # inf or inf AT or inf arty or inf AD
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
    
    def populate_data(self,entry):
        data = gdb.equip_db.equip_by_name(entry)
        self.equip_name.SetValue(data.name)
        self.nation.SetValue(data.nation)
        # new way to do this is to ENABLE the required data values
        #   then if the control is enabled, populate it
        if data.type == "AFV":
            self.equip_type.SetSelection(self.equip_type.FindString("AFV"))  
        elif data.type == "INF":
            self.equip_type.SetSelection(self.equip_type.FindString("Infantry"))
        elif data.type == "APC":
            self.equip_type.SetSelection(self.equip_type.FindString("APC"))
        elif data.type == "IFV":
            self.equip_type.SetSelection(self.equip_type.FindString("IFV"))
        elif data.type == "AT":
            self.equip_type.SetSelection(self.equip_type.FindString("AT"))
        elif data.type == "SP AT":
            self.equip_type.SetSelection(self.equip_type.FindString("SP AT"))
        elif data.type == "Artillery":
            self.equip_type.SetSelection(self.equip_type.FindString("Artillery"))
        elif data.type == "SP Artillery":
            self.equip_type.SetSelection(self.equip_type.FindString("SP Artillery"))
        elif data.type == "AD":
            self.equip_type.SetSelection(self.equip_type.FindString("AD"))
        elif data.type == "SP AD":
            self.equip_type.SetSelection(self.equip_type.FindString("SP AD"))
        
        self.disable_by_type(None)
        
        if self.op_range.IsEnabled():
            self.op_range.SetValue(str(data.range))
        if self.weight.IsEnabled():
            self.weight.SetValue(str(data.weight))
        if self.speed.IsEnabled():
            self.speed.SetValue(str(data.speed))
        if self.ammo_store.IsEnabled():
            self.ammo_store.SetValue(str(data.ammo_store))
        if self.crew.IsEnabled():
            self.crew.SetValue(str(data.crew))
        if self.armour.IsEnabled():
            self.armour.SetSelection(self.armour.FindString(data.armour))
        if self.FCE.IsEnabled():
            self.FCE.SetSelection(self.FCE.FindString(data.fire_control))
        if self.squad.IsEnabled():
            self.squad.SetValue(str(data.squad))
        if self.amph.IsEnabled():
            if data.amphibious:
                self.amph.SetValue(True)
            else:
                self.amph.SetValue(False)
        # populate the weapons list
        for i,weapon_entry in enumerate(self.weaps):
            try:
                self.weaps[i].SetValue(data.weapons[i])
            except:
                self.weaps[i].SetValue("")
                pass
        # update the OLI display for the selected value
        self.OLIDisplay.SetLabel("OLI: {:>5,.0f}".format(data.TLI))
        
    def weapons_list(self,rows,clear=True):
        # generates a list of comboboxes with rows rows
        self.weaps_box = list()
        self.weaps = list()
        weapon_choices = [""] + gdb.weaps_db.names
        for i in range(rows):
            try:
                if not clear:
                    entry = self.weaps[i].GetValue()
                else:
                    entry = ""
            except:
                entry = ""
                pass
            self.weaps_box.append(wx.BoxSizer(wx.HORIZONTAL))
            #self.weaps.append(wx.ComboBox(self.right_panel,-1,entry,choices=weapon_choices))
            self.weaps.append(MatchingCombo(self.right_panel,-1,entry,choices=weapon_choices,
                                            style=wx.TE_PROCESS_ENTER))
            self.weaps_box[-1].Add(self.weaps[-1],1,wx.ALL,0)
            self.weaps_static.Add(self.weaps_box[-1],1,wx.ALL|wx.EXPAND,0)
        self.SendSizeEvent() # forces everything to be repainted
    
    # dynamic generation of weapon list is not working currently        
    # def add_weapons_list_entry(self,event):
    #     rows = len(self.weaps_box)
    #     self.weapons_list(rows) # apparently the length is always one greater than before
    #     # self.weaps_box.append(wx.BoxSizer(wx.HORIZONTAL))
    #     # self.weaps.append(wx.ComboBox(self.right_panel,-1,"",choices=gdb.weaps_db.names))
    #     # self.weaps_box[-1].Add(self.weaps[-1],1,wx.ALL,0)
    #     # self.weaps_subsizer.Add(self.weaps_box[-1],1,wx.ALL|wx.EXPAND,0)
    # 
    # def del_weapons_list_entry(self,event):
    #     rows = len(self.weaps_box)
    #     # print(self.weaps)
    #     self.weaps_subsizer.Hide(rows)
    #     self.weaps_subsizer.Remove(rows)
    #     for entry in self.weaps:
    #         print(entry.GetValue())
    #     self.SendSizeEvent() # forces everything to be repainted
    #     #self.weapons_list(rows-1)
    
    # GUI functions
    def on_name_box(self,event):
        # when the text in the name box changes, this function will set the selection
        #   in the equipment list _if_ that name exists
        nametext = self.equip_name.GetValue()
        equip_index = self.equip_listbox.FindString(nametext)
        self.equip_listbox.SetSelection(equip_index)
        
    def on_squad_btn(self,event):
        sd = squad_dialog(self)
        sd.Show()
    
    def clear_form(self,event):
        self.equip_name.SetValue("")
        self.nation.SetValue("")
        self.equip_type.SetSelection(0)
        self.op_range.SetValue("")
        self.weight.SetValue("")
        self.speed.SetValue("")
        self.ammo_store.SetValue("")
        self.crew.SetValue("")
        self.armour.SetSelection(0)
        self.FCE.SetSelection(0)
        self.squad.SetValue("")
        self.amph.SetValue(False)
        # clear the weapons list
        for i,weapon_entry in enumerate(self.weaps):
            self.weaps[i].Set([""] + gdb.weaps_db.names) #update choices
            self.weaps[i].SetValue("")
    
    def save_equipment(self,event):
        type = self.equip_type.GetString(self.equip_type.GetSelection())
        # generic values
        name = self.equip_name.GetValue()
        nation = self.nation.GetValue() # used to make a folder
        weapons = list()
        for item in self.weaps:
            potential_weap = item.GetValue()
            if potential_weap != "":
                weapons.append(potential_weap)
        
        # check if we are going to overwrite anything
        if self.equip_listbox.FindString(name) != -1: # returns -1 if NOT_FOUND
            dlg = wx.MessageDialog(self, 
                                "Entry exists, overwrite?",
                                "Confirm overwrite", wx.YES_NO|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_NO:
                return
        
        # get the data from the form
        if self.op_range.IsEnabled():
            range = int(self.op_range.GetValue())
        if self.weight.IsEnabled():
            weight = float(self.weight.GetValue())
        if self.speed.IsEnabled():
            speed = float(self.speed.GetValue())
        if self.ammo_store.IsEnabled():
            ammo_store = int(self.ammo_store.GetValue())
        if self.crew.IsEnabled():
            crew = int(self.crew.GetValue())
        if self.armour.IsEnabled():
            armour = self.armour.GetString(self.armour.GetSelection())
        if self.FCE.IsEnabled():
            FCE = self.FCE.GetString(self.FCE.GetSelection())
        if self.squad.IsEnabled():
            squad = float(self.squad.GetValue())
        if self.amph.IsEnabled():
            amphibious = self.amph.GetValue()
        # generate the new equipment entry
        if type == "Infantry":
            new_equip = db_equipment.equipment_inf(name, weapons, ammo_store, crew)
        elif type == "AFV":
            new_equip = db_equipment.equipment_afv(name, weapons, range, weight, 
                                                    speed, ammo_store, crew, armour,
                                                    FCE, amphibious,)
        elif type == "APC":
            new_equip = db_equipment.equipment_apc(name, weapons, range, weight, speed, ammo_store,
                                                    crew, armour, squad, amphibious,)
        elif type == "IFV":
            new_equip = db_equipment.equipment_ifv(name, weapons, range, weight, speed, ammo_store,
                                                    crew, armour, FCE, squad, amphibious,)
        elif type == "AT":
            new_equip = db_equipment.equipment_infat(name, weapons, ammo_store, crew)
        elif type == "SP AT":
            new_equip = new_equip = db_equipment.equipment_spat(name, weapons, range, weight, 
                                                    speed, ammo_store, crew, armour,
                                                    amphibious,)
        elif type == "Artillery":
            new_equip = db_equipment.equipment_infarty(name, weapons, ammo_store, crew)
        elif type == "SP Artillery":
            new_equip = db_equipment.equipment_sparty(name, weapons, range, weight, 
                                                    speed, ammo_store, crew, armour,
                                                    amphibious,)
        elif type == "AD":
            new_equip = db_equipment.equipment_infad(name, weapons, ammo_store, crew)
        elif type == "SP AD":
            new_equip = db_equipment.equipment_spad(name, weapons, range, weight, 
                                                    speed, ammo_store, crew, armour,
                                                    FCE, amphibious,)
        else:
            return
        # make the directory in case it does not exist
        new_equip.nation = nation
        path = "../database/equipment/{}/".format(nation)
        os.makedirs(path, exist_ok=True)
        # output the yaml file containing the equipment
        with open("{}eqp_{}.yml".format(path,name),'w+') as f:
            yaml.dump(new_equip, f, default_flow_style=False)
        # reload the data and update the listctrl
        gdb.update_data() # reloads all the data
        self.equip_listbox.Set(gdb.equip_db.names)
    
    def load_equipment(self,event):
        selected = self.equip_listbox.GetString(self.equip_listbox.GetSelection())
        self.clear_form(None) # clear the form before loading in new data
        self.populate_data(selected)
        
    def on_new_weap(self,event):
        weap_gui = weapon_gui.weap_gui_frame(self)
        weap_gui.Show()
    
    def on_reload_db(self,event):
        gdb.update_data()
        # update the weapons list available
        for i,weapon_entry in enumerate(self.weaps):
            self.weaps[i].Set([""] + gdb.weaps_db.names) #update choices
    
    def show_info(self,event):
        info = str()
        for form in gdb.forms:
            info = info + form.GetOLI() + "\n"
        infobox = InfoForm(self,info)
        infobox.Show()
    
    def OnClose(self,event):
        dlg = wx.MessageDialog(self, 
            "Are you sure you want to close?",
            "Confirm exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

class squad_dialog(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,title="QJM Squad Dialog",
                            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)
        self.parent = parent
        
        frm_sizer = wx.BoxSizer(wx.VERTICAL)
        frm_sizer.Add(panel,1,wx.EXPAND)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # create a set of drop downs
        equip_pair_sizer = list()
        self.equip_pair_item = list()
        self.equip_pair_qty = list()
        # equipment available will be only infantry types
        eqp = [""] + gdb.equip_db.names_by_types(["INF","AT","AD"])
        for i in range(6):
            equip_pair_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
            self.equip_pair_item.append(wx.Choice(panel,-1,choices=eqp))
            equip_pair_sizer[-1].Add(self.equip_pair_item[-1],1,wx.ALL|wx.EXPAND,3)
            self.equip_pair_qty.append(wx.TextCtrl(panel,-1,""))
            equip_pair_sizer[-1].Add(self.equip_pair_qty[-1],1,wx.ALL|wx.EXPAND,3)
            main_sizer.Add(equip_pair_sizer[-1],0,wx.ALL|wx.EXPAND,5)
        # add the OK buttons
        self.tli_ctrl = wx.TextCtrl(panel,-1,"",style=wx.TE_CENTRE|wx.TE_READONLY)
        #self.tli_ctrl.Enable(False)
        self.calc_btn = wx.Button(panel,-1,"Calculate")
        self.calc_btn.Bind(wx.EVT_BUTTON, self.on_calc)
        main_sizer.Add(self.tli_ctrl,0,wx.EXPAND,5)
        main_sizer.Add(self.calc_btn,0,wx.EXPAND,5)
        
        self.ok_btn = wx.Button(panel,-1,"OK")
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        main_sizer.Add(self.ok_btn,0,wx.EXPAND,5)
        
        panel.SetSizer(main_sizer)
        self.SetSizer(frm_sizer)
        self.Fit()
    
    def on_ok(self,event):
        self.on_calc(None)
        self.Destroy()
    
    def on_calc(self,event):
        TLI = 0
        for i,item in enumerate(self.equip_pair_item):
            equipname = item.GetString(item.GetSelection())
            if equipname != "":
                equipqty = int(self.equip_pair_qty[i].GetValue())
                TLI += equipqty * gdb.equip_db.equip_by_name(equipname).TLI
        self.tli_ctrl.SetValue("TLI: "+str(int(TLI)))
        self.parent.squad.SetValue(str(int(TLI))) # set the TLI on the bottom

class InfoForm(wx.Frame):
     def __init__(self,parent,information):
        wx.Frame.__init__(self,parent,title="Information",
                            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.info_box = wx.TextCtrl(panel,-1,information,style = wx.TE_MULTILINE)
        main_sizer.Add(self.info_box,1,wx.EXPAND|wx.ALL,5)
        
        panel.SetSizerAndFit(main_sizer)
        #self.Fit()
        
if __name__ == "__main__":         
    app = wx.App()
    equip_gui = equipment_gui_frame()
    equip_gui.Show()

    app.MainLoop()