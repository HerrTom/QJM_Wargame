import os

import wx

import db_oob
import gamemaster_gui
import formation_gui
import equip_gui
import weapon_gui


# to do:
# convert gui scripts to be panels and remove references here # DONE
# move combat function out of the gamemaster gui and into its own logic
#   potentially a battle object?

# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Main_Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title="QJM Wargame",)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.gdb = db_oob.oob_db() # set the database here, accesible to the children

        nb = wx.Notebook(self)
        main_sizer.Add(nb,1,wx.ALL|wx.EXPAND)
        gm = gamemaster_gui.GamemasterWindow(nb)
        fm = formation_gui.FormationWindow(nb,self.gdb)
        eq = equip_gui.EquipmentWindow(nb,self.gdb)
        wp = weapon_gui.WeaponWindow(nb)
        nb.AddPage(gm,"Gamemaster",select=True)
        nb.AddPage(fm,"Formation Data")
        nb.AddPage(eq,"Equipment Data")
        nb.AddPage(wp,"Weapon Data")
        
        self.SetSizerAndFit(main_sizer)

    def OnClose(self,event):
        dlg = wx.MessageDialog(self, 
            "Are you sure you want to close?",
            "Confirm exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

if __name__ == "__main__":         
    app = wx.App()
    frm = Main_Frame()
    frm.Show()

    app.MainLoop()
