import wx
import time
from datetime import datetime
import ModuleClock, ModuleVastTrafik, ModuleCalender, ModuleWeather, ModuleSunriseSunset
#import os
#import psutil

class Example(wx.Frame):
    coordinates = {'Göteborg': {'lat': 57.71084, 'long': 11.99120}, 'Skellefteå': {'lat': 64.75755, 'long': 20.95051},
                   'Älvsbyn': {'lat': 65.67258, 'long': 21.03356}}
    currentCity = 'Älvsbyn'
    def __init__(self, parent, title):
        self.lastcall = datetime.now()
        super(Example, self).__init__(parent, title=title, size=(900, 750))
        self.SetBackgroundColour('Black')

        self.panel_clock = wx.Panel(self)
        self.clock = ModuleClock.ModuleClock(self.panel_clock)

        self.panel_vasttrafik = wx.Panel(self, pos=(550,0))
        self.vasttrafik = ModuleVastTrafik.ModuleVastTrafik(self.panel_vasttrafik, fontSize=10, update_freq_graphics=10, update_freq_data=80)

        self.panel_calender = wx.Panel(self, pos=(0, 150))
        self.calender = ModuleCalender.ModuleCalender(self.panel_calender, days_to_plot_in_detail=3)

        self.panel_weather = wx.Panel(self, pos=(250, 150))
        self.weather = ModuleWeather.ModuleWeather(self.panel_weather, places=self.coordinates) ##lat=[self.coordinates[self.currentCity]['lat']],
                                                   #long=[self.coordinates[self.currentCity]['long']], city=[self.currentCity])

        self.panel_sunset = wx.Panel(self)
        self.sunset = ModuleSunriseSunset.ModuleSunriseSunset(self.panel_sunset, lat=self.coordinates[self.currentCity]['lat'],
                                                              long=self.coordinates[self.currentCity]['long'])

        sizerLeft = wx.BoxSizer(wx.VERTICAL)
        sizerRight = wx.BoxSizer(wx.VERTICAL)
        sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        sizerLeft.Add(self.panel_clock, 0, wx.ALL , 5)
        sizerLeft.Add(self.panel_calender, 0, wx.ALL| wx.ALIGN_TOP, 5)

        sizerRight.Add(self.panel_weather, 0, wx.ALL| wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)
        sizerRight.Add(self.panel_sunset, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)
        sizerRight.Add(self.panel_vasttrafik, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)

        sizerMain.Add(sizerLeft, 1, wx.ALL | wx.ALIGN_RIGHT , 5)
        sizerMain.Add(sizerRight, 1, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)

        self.SetSizer(sizerMain)
        self.Fit()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tick, self.timer)
        self.timer.Start(500)

        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

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

        self.weather.do_update()
        #if (now - self.weather.updated_graphics).seconds >= self.weather.update_freq_graphics:
        #    self.weather.update()

        #if (now - self.weather.updated_data).seconds >= self.weather.update_freq_data:
        #    self.weather.updateDataSet()

        self.clock.update()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE or keycode== wx.WXK_RETURN:
            print("you pressed the spacebar!")
            self.ShowFullScreen(True)
            event.Skip()
        elif keycode == wx.WXK_ESCAPE:
            print("you pressed the escape button!")
            self.ShowFullScreen(False)
            event.Skip()



        # Check memory use by process every 30 seconds
 #       if (now - self.lastcall).seconds > 10:
 #           process = psutil.Process(os.getpid())
 #           print('memory use =', process.memory_info().rss / 1000, 'kb')
 #           self.lastcall = now





app = wx.App()
Example(None, title='FlexiGrid Demo')
app.MainLoop()