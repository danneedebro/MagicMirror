from datetime import datetime
import wx
import wx.lib.stattext as ST
import pytz
from ModuleBase import ModuleBase


class ModuleClock(ModuleBase):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.font1 = wx.Font(72, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.font2 = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)

        self.UpdateGraphics()

    def UpdateCheck(self):
        if self.lastUpdateGraphics.minute != datetime.now().minute:
            super().UpdateCheck(updateGraphicsNow = True)

    def UpdateGraphics(self):
        super().UpdateGraphics()

        panel = wx.Panel(self)
        panel.SetBackgroundColour('Black')
        now = pytz.timezone('Europe/Stockholm').localize(datetime.now())
        #now = datetime.now()
        lbl_date = ST.GenStaticText(panel, label=now.strftime('%Y-%m-%d'), style=wx.ALIGN_LEFT)
        lbl_date.SetBackgroundColour('Black')
        lbl_date.SetForegroundColour('White')

        lbl_week = ST.GenStaticText(panel, label=now.strftime('v. %V'), style=wx.ALIGN_RIGHT)
        lbl_week.SetBackgroundColour('Black')
        lbl_week.SetForegroundColour('White')
        
        lbl_time = ST.GenStaticText(panel, label=now.strftime('%H:%M'))
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
        self.Fit()
        self.Thaw()
