import wx
import yaml
from fuzzywuzzy import process

import db_formation


class MatchingCombo(wx.ComboBox):
    def __init__(self,*args, **kwargs):
        # init the combo box
        wx.ComboBox.__init__(self,*args,**kwargs)
        # as long as 
        self.Bind(wx.EVT_TEXT_ENTER,self.CheckItems)
        #self.Bind(wx.EVT_KILL_FOCUS,self.CheckItems)
        
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
        event.Skip()

class FormationWindow(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent,)

        frame_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # panel on the left will have the ListBox and new/copy/save buttons
        left_panel = wx.Panel(self,)
        lp_sizer = wx.BoxSizer(wx.VERTICAL)
        lp_staticsizer = wx.StaticBoxSizer(wx.VERTICAL,left_panel,"Formations:")
        lp_sizer.Add(lp_staticsizer, 1, wx.ALL, 3)

        # formation list
        self.form_listbox = wx.ListBox(left_panel,-1, choices=self.GetTopLevelParent().gdb.gm_forms_db.names,
                                        style=wx.LB_ALWAYS_SB,size=(250,-1))
        self.form_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_formation)
        lp_staticsizer.Add(self.form_listbox, 1, wx.ALL|wx.EXPAND, 3)
        self.form_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_formation)


        # right hand panel has all the data for the entry
        self.right_panel = wx.ScrolledWindow(self)
        rp_sizer = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Formation Entry:")
        # set up the scroll bar
        self.right_panel.SetScrollRate(0,5)

        # formation name
        self.form_name = wx.TextCtrl(self.right_panel,-1,'')
        form_name_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Name:")
        form_name_static.Add(self.form_name,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(form_name_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)

        # equipment quantities
        self.equip_list_static = wx.StaticBoxSizer(wx.VERTICAL,self.right_panel,"Equipment:")
        rp_sizer.Add(self.equip_list_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)
        self.equip_sizers = list()
        self.equip_types = list()
        self.equip_qtys = list()

        self.add_equip_item()



        # wrap up the gui
        left_panel.SetSizer(lp_sizer)
        self.right_panel.SetSizer(rp_sizer)
        frame_sizer.Add(left_panel, 0, wx.EXPAND)
        frame_sizer.Add(self.right_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)

    def load_formation(self,event):
        selected = self.form_listbox.GetString(self.form_listbox.GetSelection())
        new_formation = self.GetTopLevelParent().gdb.gm_forms_db.formation_by_name(selected)
        self.form_name.SetValue(new_formation.name)
        # delete all the existing equipment stuff
        self.remove_all_equip()
        for equip, qty in new_formation.equipment.items():
            self.add_equip_item(equip=equip,qty=qty)
        # add a blank entry to the end
        self.add_equip_item()
        self.Layout()


    def remove_all_equip(self):
        for i in range(len(self.equip_types)):
            self.equip_types[-1].Destroy()
            self.equip_qtys[-1].Destroy()
            del self.equip_types[-1]
            del self.equip_qtys[-1]
        self.Layout()

    def OnFilled(self,event):
        # check if the last entry is empty
        if self.equip_types[-1].GetValue() != "":
            self.add_equip_item()
        else: # last entry is not empty
            if len(self.equip_types) > 1:
                if self.equip_types[-2].GetValue() == "":
                    # destroy the UI elements
                    self.equip_types[-1].Destroy()
                    self.equip_qtys[-1].Destroy()
                    # delete the list elements
                    del self.equip_types[-1]
                    del self.equip_qtys[-1]
        self.Layout()
        event.Skip()

    def add_equip_item(self,equip="",qty=""):
        equips = self.GetTopLevelParent().gdb.equip_db.names
        self.equip_sizers.append(wx.BoxSizer(wx.HORIZONTAL))
        self.equip_types.append(MatchingCombo(self.right_panel,-1,equip,choices=equips,
                                            style=wx.TE_PROCESS_ENTER))
        self.equip_qtys.append(wx.TextCtrl(self.right_panel,-1,str(qty)))
        # bind the equip type to OnFilled
        self.equip_types[-1].Bind(wx.EVT_KILL_FOCUS,self.OnFilled)
        # append the items to the list
        self.equip_sizers[-1].Add(self.equip_types[-1],1,wx.ALL|wx.EXPAND,1)
        self.equip_sizers[-1].Add(self.equip_qtys[-1],0,wx.ALL|wx.EXPAND,1)
        self.equip_list_static.Add(self.equip_sizers[-1],1,wx.ALL|wx.EXPAND,0)

        #self.Layout()