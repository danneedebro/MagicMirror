#   -----------------------------
#   |DATE         |         WEEK|
#   -----------------------------
#   |           TIME            |
#   |                           |
#   -----------------------------


from datetime import datetime
import wx


class ModuleClock:
    def __init__(self, panel_main):
        self.panel_main = panel_main

        self.font1 = wx.Font(72, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.font2 = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)

        self.last_update = datetime.now()
        self.update()

    def update_check(self):
        if self.last_update.minute != datetime.now().minute:
            self.update()

    def update(self):
        self.last_update = datetime.now()
        self.panel_main.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.panel_main.GetChildren():
            myobj.Destroy()

        panel = wx.Panel(self.panel_main)
        panel.SetBackgroundColour('Black')

        now = datetime.now()
        lbl_date = wx.StaticText(panel, label=now.strftime('%Y-%m-%d'), style=wx.ALIGN_LEFT)
        lbl_date.SetBackgroundColour('Black')
        lbl_date.SetForegroundColour('White')

        lbl_week = wx.StaticText(panel, label=now.strftime('v. %W'), style=wx.ALIGN_RIGHT)
        lbl_week.SetBackgroundColour('Black')
        lbl_week.SetForegroundColour('White')
        
        lbl_time = wx.StaticText(panel, label=now.strftime('%H:%M'))
        lbl_time.SetBackgroundColour('Black')
        lbl_time.SetForegroundColour('White')

        lbl_time.SetFont(self.font1)
        lbl_date.SetFont(self.font2)
        lbl_week.SetFont(self.font2)

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_one = wx.BoxSizer(wx.HORIZONTAL)

        sizer_one.Add(lbl_date, 1, wx.ALL, 0)
        sizer_one.Add(lbl_week, 1, wx.ALIGN_RIGHT, 0)

        sizer_main.Add(sizer_one, 0, wx.ALL, 0)
        sizer_main.Add(lbl_time, 0, wx.ALL | wx.EXPAND, 0)

        panel.SetSizer(sizer_main)
        panel.Fit()
        self.panel_main.Fit()
        self.panel_main.Thaw()
