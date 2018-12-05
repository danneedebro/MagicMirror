import wx
import time
from datetime import datetime
import ModuleClock, ModuleVastTrafik, ModuleCalender
#import os
#import psutil

class Example(wx.Frame):

    def __init__(self, parent, title):
        self.lastcall = datetime.now()
        super(Example, self).__init__(parent, title=title, size=(900, 750))
        self.SetBackgroundColour('Black')

        self.panel_clock = wx.Panel(self, pos=(0,0))#, size=(400,300))
        self.clock = ModuleClock.ModuleClock(self.panel_clock)

        self.panel_vasttrafik = wx.Panel(self, pos=(550,0))#, size=(400,300))
        self.vasttrafik = ModuleVastTrafik.ModuleVastTrafik(self.panel_vasttrafik, update_freq_graphics=10, update_freq_data=80)

        self.panel_calender = wx.Panel(self, pos=(0, 150))  # , size=(400,300))
        self.calender = ModuleCalender.ModuleCalender(self.panel_calender, update_freq_graphics=10, update_freq_data=90)


        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tick, self.timer)
        self.timer.Start(500)
        self.Show()


    def tick(self, ev):
        now = datetime.now()

        if (now - self.vasttrafik.updated_graphics).seconds >= self.vasttrafik.update_freq_graphics:
            self.vasttrafik.update()

        if (now - self.vasttrafik.updated_data).seconds >= self.vasttrafik.update_freq_data:
            self.vasttrafik.updateDataSet()

        if (now - self.calender.updated_graphics).seconds >= self.calender.update_freq_graphics:
            self.calender.update()

        if (now - self.calender.updated_data).seconds >= self.calender.update_freq_data:
            self.calender.updateDataSet()

        self.clock.update()




        # Check memory use by process every 30 seconds
 #       if (now - self.lastcall).seconds > 10:
 #           process = psutil.Process(os.getpid())
 #           print('memory use =', process.memory_info().rss / 1000, 'kb')
 #           self.lastcall = now





app = wx.App()
Example(None, title='FlexiGrid Demo')
app.MainLoop()