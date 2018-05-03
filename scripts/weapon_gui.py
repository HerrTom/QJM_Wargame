
import wx
import os
import yaml

import db_oob
import db_weapons


atgm_choices = ['SACLOS wire day','SACLOS wire day/night','SACLOS radio',
                            'LOSLBR','F&F',]
aam_choices = ['Optical','BR','IR','SARH','ARH']

#class weap_gui_frame(wx.Frame):
class WeaponWindow(wx.Panel):
    def __init__(self,parent):
        #wx.Frame.__init__(self,parent,title="QJM Weapon Editor")
        wx.Panel.__init__(self,parent,)
        #self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # panel on the left will have the ListBox and new/copy/save buttons
        left_panel = wx.Panel(self,)
        lp_sizer = wx.BoxSizer(wx.VERTICAL)
        lp_staticsizer = wx.StaticBoxSizer(wx.VERTICAL,left_panel,"Weapons:")
        lp_sizer.Add(lp_staticsizer, 1, wx.ALL, 3)

        # equipment list
        self.weap_listbox = wx.ListBox(left_panel,-1, choices=self.GetTopLevelParent().gdb.weaps_db.names,
                                        style=wx.LB_ALWAYS_SB,size=(180,-1))
        lp_staticsizer.Add(self.weap_listbox, 1, wx.ALL|wx.EXPAND, 3)
        
        self.weap_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_weapon)
        
        # OLI value
        self.TLIDisplay = wx.StaticText(left_panel,-1,"TLI: {:>5,.0f}".format(0))
        lp_sizer.Add(self.TLIDisplay,0,wx.CENTER,5)
        
        # buttons
        self.new_button = wx.Button(left_panel, -1,"New",)
        self.save_button = wx.Button(left_panel, -1,"Save",)
        
        self.new_button.Bind(wx.EVT_BUTTON, self.clear_data)
        self.save_button.Bind(wx.EVT_BUTTON, self.save_weapon)
        
        lp_sizer.Add(self.new_button,  0, wx.ALL|wx.EXPAND, 3)
        lp_sizer.Add(self.save_button, 0, wx.ALL|wx.EXPAND, 3)
        
        
        # right hand panel has all the data for the entry
        self.right_panel = wx.ScrolledWindow(self)
        rp_sizer = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Weapon Entry:")
        # set up the scroll bar
        self.right_panel.SetScrollRate(0,5)
        
        # weap name entry
        self.weap_name = wx.TextCtrl(self.right_panel,-1,'')
        weap_name_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Name:")
        weap_name_static.Add(self.weap_name,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_name_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # bind the event handler that will search for existing names and highlight if a hit
        self.weap_name.Bind(wx.EVT_TEXT, self.on_name_box)
        
        # type:
        type_choices = ["Gun","Automatic gun","ATGM","AAM","Bomb"]
        self.weap_type = wx.Choice(self.right_panel,-1,choices=type_choices)
        weap_type_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Weapon Type:")
        weap_type_static.Add(self.weap_type,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_type_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        self.weap_type.Bind(wx.EVT_CHOICE, self.disable_by_type)
        
        # Entries exist for:
        # name,
        # type (for filter)
        # range,
        # accuracy,
        # rie,
        # rof,
        # rf_multiple,
        # barrels,
        # calibre,
        # muzzle_vel,
        # ammo,
        # min_range,
        # penetration,
        # guidance,
        # enhancement
        
        # range:
        self.weap_range = wx.TextCtrl(self.right_panel,-1,'')
        weap_range_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Range:")
        weap_range_static.Add(self.weap_range,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_range_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # accuracy
        self.weap_accuracy = wx.TextCtrl(self.right_panel,-1,'')
        weap_accuracy_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Accuracy:")
        weap_accuracy_static.Add(self.weap_accuracy,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_accuracy_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # rie
        self.weap_rie = wx.TextCtrl(self.right_panel,-1,'')
        weap_rie_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Relative Incapacitation Effect:")
        weap_rie_static.Add(self.weap_rie,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_rie_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # rof
        self.weap_rof = wx.TextCtrl(self.right_panel,-1,'')
        weap_rof_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Rate of Fire:")
        self.weap_rf_mult = wx.CheckBox(self.right_panel,-1,'Crew served')
        weap_rof_static.Add(self.weap_rof,0,wx.ALL|wx.EXPAND,3)
        weap_rof_static.Add(self.weap_rf_mult,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_rof_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # barrels:
        self.weap_barrels = wx.TextCtrl(self.right_panel,-1,'')
        weap_barrels_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Barrels:")
        weap_barrels_static.Add(self.weap_barrels,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_barrels_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # calibre:
        self.weap_calibre = wx.TextCtrl(self.right_panel,-1,'')
        weap_calibre_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Calibre:")
        weap_calibre_static.Add(self.weap_calibre,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_calibre_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # muzzle_vel:
        self.weap_muzzle_vel = wx.TextCtrl(self.right_panel,-1,'')
        weap_muzzle_vel_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,
                                                    "Muzzle/Flight Velocity:")
        weap_muzzle_vel_static.Add(self.weap_muzzle_vel,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_muzzle_vel_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # ammo:
        self.weap_ammo = wx.TextCtrl(self.right_panel,-1,'')
        weap_ammo_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Ammo name:")
        weap_ammo_static.Add(self.weap_ammo,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_ammo_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # min_range:
        self.weap_min_range = wx.TextCtrl(self.right_panel,-1,'')
        weap_min_range_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Minimum range:")
        weap_min_range_static.Add(self.weap_min_range,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_min_range_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # guidance:
        guidance_choices = atgm_choices
        self.weap_guidance = wx.Choice(self.right_panel,-1,choices=guidance_choices)
        weap_guidance_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Guidance:")
        weap_guidance_static.Add(self.weap_guidance,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_guidance_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # penetration:
        self.weap_penetration = wx.TextCtrl(self.right_panel,-1,'')
        weap_penetration_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Penetration:")
        weap_penetration_static.Add(self.weap_penetration,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_penetration_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # enhancement:
        self.weap_enhancement = wx.TextCtrl(self.right_panel,-1,'')
        weap_enhancement_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,
                                                    "Enhancement Factor:")
        weap_enhancement_static.Add(self.weap_enhancement,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(weap_enhancement_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        
        # wrap up the gui
        left_panel.SetSizer(lp_sizer)
        self.right_panel.SetSizer(rp_sizer)
        frame_sizer.Add(left_panel, 0, wx.EXPAND)
        frame_sizer.Add(self.right_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)
        self.SetSize((400,500))
    
    # Functions
    
    def disable_all(self):
        # function to disable all non-common elements
        self.weap_range.Enable(False)
        self.weap_rie.Enable(False)
        self.weap_barrels.Enable(False)
        self.weap_muzzle_vel.Enable(False)
        self.weap_accuracy.Enable(False)
        self.weap_rof.Enable(False)
        self.weap_rf_mult.Enable(False)
        self.weap_min_range.Enable(False)
        self.weap_penetration.Enable(False)
        self.weap_guidance.Enable(False)
        self.weap_enhancement.Enable(False)
    
    def disable_by_type(self, event):
        self.disable_all()
        # currently only atgm type enables disabled spaces
        weaptype = self.weap_type.GetString(self.weap_type.GetSelection())
        if weaptype == "ATGM":
            self.weap_range.Enable(True)
            self.weap_muzzle_vel.Enable(True)
            self.weap_rie.Enable(True)
            self.weap_barrels.Enable(True)
            self.weap_min_range.Enable(True)
            self.weap_penetration.Enable(True)
            self.weap_guidance.Enable(True)
            self.weap_enhancement.Enable(True)
            self.weap_guidance.Set(atgm_choices)
        elif weaptype == "AAM":
            self.weap_range.Enable(True)
            self.weap_muzzle_vel.Enable(True)
            self.weap_barrels.Enable(True)
            self.weap_min_range.Enable(True)
            self.weap_guidance.Enable(True)
            self.weap_enhancement.Enable(True)
            self.weap_guidance.Set(aam_choices)
        elif weaptype == "Automatic gun":
            self.weap_range.Enable(True)
            self.weap_rie.Enable(True)
            self.weap_barrels.Enable(True)
            self.weap_muzzle_vel.Enable(True)
            self.weap_accuracy.Enable(True)
            self.weap_rof.Enable(True)
            self.weap_rf_mult.Enable(True)
        elif weaptype == "Bomb":
            self.weap_accuracy.Enable(True)
        else:
            self.weap_accuracy.Enable(True)
            self.weap_range.Enable(True)
            self.weap_rie.Enable(True)
            self.weap_barrels.Enable(True)
            self.weap_muzzle_vel.Enable(True)
    
    def clear_data(self,event):
        self.weap_name.SetValue("")
        self.weap_type.SetSelection(0)
        self.weap_range.SetValue("")
        self.weap_accuracy.SetValue("")
        self.weap_rie.SetValue("")
        self.weap_rof.SetValue("")
        self.weap_rf_mult.SetValue(False)
        self.weap_barrels.SetValue("")
        self.weap_calibre.SetValue("")
        self.weap_muzzle_vel.SetValue("")
        self.weap_ammo.SetValue("")
        self.weap_min_range.SetValue("")
        self.weap_penetration.SetValue("")
        self.weap_guidance.SetSelection(0)
        self.weap_enhancement.SetValue("")
        # when the data clears, update the database
        self.GetTopLevelParent().gdb.update_data() # reloads all the data
    
    def populate_data(self,entry):
        self.clear_data(None)
        data = self.GetTopLevelParent().gdb.weaps_db.weap_by_name(entry)
        self.weap_name.SetValue(data.name)
        if data.type == "Automatic gun":
            self.weap_type.SetSelection(self.weap_type.FindString("Automatic gun"))
        elif data.type == "ATGM":
            self.weap_type.SetSelection(self.weap_type.FindString("ATGM"))
        elif data.type == "AAM":
            self.weap_type.SetSelection(self.weap_type.FindString("AAM"))
        elif data.type == "Bomb":
            self.weap_type.SetSelection(self.weap_type.FindString("Bomb"))
        else: # default is GUN type
            self.weap_type.SetSelection(self.weap_type.FindString("Gun"))
        self.disable_by_type(None)

        if self.weap_range.IsEnabled():
            self.weap_range.SetValue(str(data.range))
        if self.weap_accuracy.IsEnabled():
            self.weap_accuracy.SetValue(str(data.accuracy))
        if self.weap_rie.IsEnabled():
            self.weap_rie.SetValue(str(data.rie))
        if self.weap_rof.IsEnabled():
            self.weap_rof.SetValue(str(data.rate_of_fire))
        if self.weap_rf_mult.IsEnabled():
            if data.rf_multiple == 4:
                self.weap_rf_mult.SetValue(True)
            else:
                self.weap_rf_mult.SetValue(False)
        if self.weap_barrels.IsEnabled():
            self.weap_barrels.SetValue(str(data.barrels))
        if self.weap_calibre.IsEnabled():
            self.weap_calibre.SetValue(str(data.calibre))
        if self.weap_muzzle_vel.IsEnabled():
            self.weap_muzzle_vel.SetValue(str(data.muzzle_vel))
        if self.weap_ammo.IsEnabled():
            self.weap_ammo.SetValue(str(data.ammo))
        if self.weap_min_range.IsEnabled():
            self.weap_min_range.SetValue(str(data.min_range))
        if self.weap_penetration.IsEnabled():
            self.weap_penetration.SetValue(str(data.penetration))
        if self.weap_guidance.IsEnabled():
            self.weap_guidance.SetSelection(self.weap_guidance.FindString(data.guidance))
        if self.weap_enhancement.IsEnabled():
            self.weap_enhancement.SetValue(str(data.enhancement))
        # update the TLI
        self.TLIDisplay.SetLabel("TLI: {:>9,.0f}".format(data.TLI))
    
    def load_weapon(self,event):
        selected = self.weap_listbox.GetString(self.weap_listbox.GetSelection())
        self.populate_data(selected)
    
    def save_weapon(self,event):
        type = self.weap_type.GetString(self.weap_type.GetSelection())
        # generic values
        name = self.weap_name.GetValue()
        
        # check if we are going to overwrite anything
        if self.weap_listbox.FindString(name) != -1: # returns -1 if NOT_FOUND
            dlg = wx.MessageDialog(self, 
                                "Entry exists, overwrite?",
                                "Confirm overwrite", wx.YES_NO|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_NO:
                return
        
        if self.weap_range.IsEnabled():
            range = int(self.weap_range.GetValue())
        if self.weap_accuracy.IsEnabled():
            accuracy = float(self.weap_accuracy.GetValue())
        if self.weap_rie.IsEnabled():
            rie = float(self.weap_rie.GetValue())
        if self.weap_rof.IsEnabled():
            rof = int(self.weap_rof.GetValue())
        if self.weap_rf_mult.IsEnabled():
            if self.weap_rf_mult.GetValue():
                rf_multiple = 4
            else:
                rf_multiple = 2
        if self.weap_barrels.IsEnabled():
            barrels = int(self.weap_barrels.GetValue())
        if self.weap_calibre.IsEnabled():
            calibre = float(self.weap_calibre.GetValue())
        if self.weap_muzzle_vel.IsEnabled():
            muzzle_vel = float(self.weap_muzzle_vel.GetValue())
        if self.weap_ammo.IsEnabled():
            ammo = self.weap_ammo.GetValue()
        if self.weap_min_range.IsEnabled():
            min_range = float(self.weap_min_range.GetValue())
        if self.weap_penetration.IsEnabled():
            penetration = float(self.weap_penetration.GetValue())
        if self.weap_guidance.IsEnabled():
            guidance = self.weap_guidance.GetString(self.weap_guidance.GetSelection())
        if self.weap_enhancement.IsEnabled():
            enhancement = float(self.weap_enhancement.GetValue())
        
        if type == "ATGM":
            new_equip = db_weapons.weapon_atgm(name,
                                                range,
                                                rie,
                                                barrels,
                                                calibre,
                                                muzzle_vel,
                                                ammo,
                                                min_range,
                                                penetration,
                                                guidance,
                                                enhancement,)
        elif type == "AAM":
            new_equip = db_weapons.weapon_aam(name,
                                                range,
                                                barrels,
                                                calibre,
                                                muzzle_vel,
                                                ammo,
                                                min_range,
                                                guidance,
                                                enhancement,)
        elif type == "Automatic gun":
            new_equip = db_weapons.weapon_autogun(name,
                                                range,
                                                accuracy,
                                                rie,
                                                rof,
                                                rf_multiple,
                                                barrels,
                                                calibre,
                                                muzzle_vel,
                                                ammo,)
        elif type == "Gun":
            new_equip = db_weapons.weapon_gun(name,
                                                range,
                                                accuracy,
                                                rie,
                                                barrels,
                                                calibre,
                                                muzzle_vel,
                                                ammo,)
        elif type == "Bomb":
            new_equip = db_weapons.weapon_bomb(name,accuracy,calibre,ammo,)
        print(new_equip)
        path = "../database/weapons/"
        os.makedirs(path, exist_ok=True)
        # output the yaml file containing the equipment
        with open("{}weap_{}.yml".format(path,name),'w+') as f:
            yaml.dump(new_equip, f, default_flow_style=False)
        # reload the data and update the listctrl
        self.GetTopLevelParent().gdb.update_data() # reloads all the data
        self.weap_listbox.Set(self.GetTopLevelParent().gdb.weaps_db.names)
        self.disable_by_type(None)
    
    def on_name_box(self,event):
        # when the text in the name box changes, this function will set the selection
        #   in the weapons list _if_ that name exists
        nametext = self.weap_name.GetValue()
        weap_index = self.weap_listbox.FindString(nametext)
        self.weap_listbox.SetSelection(weap_index)   
        
    def OnClose(self,event):
        dlg = wx.MessageDialog(self, 
            "Are you sure you want to close?",
            "Confirm exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
