import wx
import wx.lib.agw.ultimatelistctrl as ULC
import yaml

import db_formation

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
        lp_staticsizer.Add(self.form_listbox, 1, wx.ALL|wx.EXPAND, 3)
        self.form_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.load_formation)


        # right hand panel has all the data for the entry
        right_panel = wx.ScrolledWindow(self)
        rp_sizer = wx.StaticBoxSizer(wx.VERTICAL,right_panel,"Formation Entry:")
        # set up the scroll bar
        right_panel.SetScrollRate(0,5)

        # formation name
        self.form_name = wx.TextCtrl(right_panel,-1,'')
        form_name_static = wx.StaticBoxSizer(wx.VERTICAL,right_panel,"Name:")
        form_name_static.Add(self.form_name,0,wx.ALL|wx.EXPAND,3)
        rp_sizer.Add(form_name_static,0,wx.LEFT|wx.RIGHT|wx.EXPAND,3)


        # wrap up the gui
        left_panel.SetSizer(lp_sizer)
        right_panel.SetSizer(rp_sizer)
        frame_sizer.Add(left_panel, 0, wx.EXPAND)
        frame_sizer.Add(right_panel, 1, wx.EXPAND)
        self.SetSizerAndFit(frame_sizer)

    def load_formation(self,event):
        pass