#   -----------------------------
#   |DATE         |         WEEK|
#   -----------------------------
#   |           TIME            |
#   |                           |
#   -----------------------------


from datetime import datetime
import wx
import time

class ModuleClock:
    def __init__(self, mainPanel):
        self.mainPanel = mainPanel
        self.update()

    def update(self):
        self.mainPanel.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            myobj.Destroy()

        panel = wx.Panel(self.mainPanel)
        panel.SetBackgroundColour('Black')
        panel.Freeze()

        now = datetime.now()
        LblDate = wx.StaticText(panel, label=now.strftime('%Y-%m-%d'), style=wx.ALIGN_LEFT)
        LblDate.SetBackgroundColour('Black')
        LblDate.SetForegroundColour('White')

        LblWeek = wx.StaticText(panel, label=now.strftime('v. %W'), style=wx.ALIGN_RIGHT)
        LblWeek.SetBackgroundColour('Black')
        LblWeek.SetForegroundColour('White')
        
        LblTime = wx.StaticText(panel, label=now.strftime('%H:%M'))
        LblTime.SetBackgroundColour('Black')
        LblTime.SetForegroundColour('White')

        font1 = wx.Font(72, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        font2 = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        LblTime.SetFont(font1)
        LblDate.SetFont(font2)
        LblWeek.SetFont(font2)

        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerOne = wx.BoxSizer(wx.HORIZONTAL)

        sizerOne.Add(LblDate, 1, wx.ALL, 0)
        sizerOne.Add(LblWeek, 1, wx.ALIGN_RIGHT, 0)

        sizerMain.Add(sizerOne, 0, wx.ALL, 0)
        sizerMain.Add(LblTime, 0, wx.ALL, 0)

        panel.SetSizer(sizerMain)
        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()
        self.mainPanel.Thaw()
        
        LblTime.Refresh()



