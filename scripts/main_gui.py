import wx
import os
import yaml

import oob
import db_formation
import db_weapons
import db_equipment

# GUI script for creating database entries


# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Equipment editor frame
class equipment_gui_frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title="QJM Equipment Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # panel on the left will have the ListBox and new/copy/save buttons
        left_panel = wx.Panel(self,)
        lp_sizer = wx.BoxSizer(wx.VERTICAL)
        lp_staticsizer = wx.StaticBoxSizer(wx.VERTICAL,left_panel,"Equipment:")
        lp_sizer.Add(lp_staticsizer, 1, wx.ALL, 3)

        # equipment list
        self.equip_listbox = wx.ListBox(left_panel,-1, choices=gbd.equip_db.names,
                                        style=wx.LB_ALWAYS_SB,size=(100,-1))
        lp_staticsizer.Add(self.equip_listbox, 1, wx.ALL|wx.EXPAND, 3)
        
        self.equip_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_equipment)
        
        # buttons
        self.new_button = wx.Button(left_panel, -1,"New",)
        self.save_button = wx.Button(left_panel, -1,"Save",)
        
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
        equip_type_choices = ["Infantry", "PC", "AFV","Infantry AT","Mobile AT",
                                "Artillery","Air defense"] # defines available choices
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
        self.weapons_list(6)
        
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
        
        # fire control
        squad_static = wx.StaticBoxSizer(wx.HORIZONTAL,self.right_panel,"Mounted squad:")
        self.squad = wx.TextCtrl(self.right_panel,-1,"")
        squad_static.Add(self.squad,1,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(squad_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # disable everything by default
        self.disable_all()
        
        # wrap up the gui
        left_panel.SetSizer(lp_sizer)
        self.right_panel.SetSizer(rp_sizer)
        frame_sizer.Add(left_panel, 0, wx.EXPAND)
        frame_sizer.Add(self.right_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)
        self.SetSize((350,500))
        
    
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
        elif type == "PC":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.FCE.Enable(True)
            self.squad.Enable(True)
        if type == "Mobile AT":
            self.op_range.Enable(True)
            self.weight.Enable(True)
            self.speed.Enable(True)
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
            self.armour.Enable(True)
            self.FCE.Enable(True)
        else: # inf or inf AT
            self.ammo_store.Enable(True)
            self.crew.Enable(True)
    
    def populate_data(self,entry):
        data = gbd.equip_db.equip_by_name(entry)
        self.equip_name.SetValue(data.name)
        self.nation.SetValue(data.nation)
        # new way to do this is to ENABLE the required data values
        #   then if the control is enabled, populate it
        if data.type == "AFV":
            self.equip_type.SetSelection(self.equip_type.FindString("AFV"))  
        elif data.type == "INF":
            self.equip_type.SetSelection(self.equip_type.FindString("Infantry"))
        elif data.type == "PC":
            self.equip_type.SetSelection(self.equip_type.FindString("PC"))
        elif data.type == "INF AT":
            self.equip_type.SetSelection(self.equip_type.FindString("Infantry AT"))
        elif data.type == "AFV AT":
            self.equip_type.SetSelection(self.equip_type.FindString("Mobile AT"))
        
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
        # populate the weapons list
        for i,weapon_entry in enumerate(self.weaps):
            try:
                self.weaps[i].SetValue(data.weapons[i])
            except:
                self.weaps[i].SetValue("")
                pass
        # after everything, run the disable function
        
    def weapons_list(self,rows):
        # generates a list of comboboxes with rows rows
        self.weaps_box = list()
        self.weaps = list()
        for i in range(rows):
            try:
                entry = self.weaps[i].GetValue()
            except:
                entry = ""
                pass
            self.weaps_box.append(wx.BoxSizer(wx.HORIZONTAL))
            self.weaps.append(wx.ComboBox(self.right_panel,-1,entry,choices=gbd.weaps_db.names))
            self.weaps_box[-1].Add(self.weaps[-1],1,wx.ALL,0)
            self.weaps_static.Add(self.weaps_box[-1],1,wx.ALL|wx.EXPAND,0)
        self.SendSizeEvent() # forces everything to be repainted
    
    # dynamic generation of weapon list is not working currently        
    # def add_weapons_list_entry(self,event):
    #     rows = len(self.weaps_box)
    #     self.weapons_list(rows) # apparently the length is always one greater than before
    #     # self.weaps_box.append(wx.BoxSizer(wx.HORIZONTAL))
    #     # self.weaps.append(wx.ComboBox(self.right_panel,-1,"",choices=gbd.weaps_db.names))
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
        
    
    def save_equipment(self,event):
        # Choices are:
        #   ["Infantry", "PC", "AFV","Infantry AT","Mobile AT","Artillery","Air defense"]
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
        if self.equip_listbox.FindString(name) == -1:
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
        if type == "Infantry":
            new_equip = db_equipment.equipment_inf(name, weapons, ammo_store, crew)
        elif type == "AFV":
            new_equip = db_equipment.equipment_afv(name, weapons, range, weight, 
                                                    speed, ammo_store, crew, armour, FCE)
        else:
            new_equip = None
        # make the directory in case it does not exist
        new_equip.nation = nation
        path = "../database/equipment/{}/".format(nation)
        os.makedirs(path, exist_ok=True)
        # output the yaml file containing the equipment
        with open("{}eqp_{}.yml".format(path,name),'w+') as f:
            yaml.dump(new_equip, f, default_flow_style=False)
        # reload the data and update the listctrl
        gbd.update_data() # reloads all the data
        self.equip_listbox.Set(gbd.equip_db.names)
    
    def load_equipment(self,event):
        selected = self.equip_listbox.GetString(self.equip_listbox.GetSelection())
        self.populate_data(selected)
    
    def OnClose(self,event):
        dlg = wx.MessageDialog(self, 
            "Are you sure you want to close?",
            "Confirm exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
# global database
global gdb
gbd = oob.oob_db()


app = wx.App()
top = equipment_gui_frame()
top.Show()
app.MainLoop()