import wx
from datetime import datetime
import ModuleClock, ModuleVastTrafik, ModuleCalender, ModuleWeather, ModuleSunriseSunset
# import os
# import psutil


class Example(wx.Frame):
    coordinates = {'Göteborg': {'lat': 57.71084, 'long': 11.99120, 'duration': 3},
                   'Skellefteå': {'lat': 64.75755, 'long': 20.95051, 'duration': 3},
                   'Älvsbyn': {'lat': 65.67258, 'long': 21.03356, 'duration': 10}}
    currentCity = 'Älvsbyn'

    def __init__(self, parent, title):
        self.lastcall = datetime.now()
        super(Example, self).__init__(parent, title=title, size=(900, 750))
        self.SetBackgroundColour('Black')

        panel_clock = wx.Panel(self)
        self.clock = ModuleClock.ModuleClock(panel_clock)

        panel_vasttrafik = wx.Panel(self)
        self.vasttrafik = ModuleVastTrafik.ModuleVastTrafik(panel_vasttrafik, fontSize=10,
                                                            update_freq_graphics=10, update_freq_data=80)

        panel_calender = wx.Panel(self)
        self.calender = ModuleCalender.ModuleCalender(panel_calender, days_to_plot_in_detail=3)

        cities = {'Älvsbyn', 'Skellefteå'}
        filtered = dict(zip(cities, [self.coordinates[k] for k in cities]))
        panel_weather = wx.Panel(self)
        self.weather = ModuleWeather.ModuleWeather(panel_weather, places=filtered)

        panel_sunset = wx.Panel(self)
        self.sunset = ModuleSunriseSunset.ModuleSunriseSunset(panel_sunset,
                                                              lat=self.coordinates[self.currentCity]['lat'],
                                                              long=self.coordinates[self.currentCity]['long'])

        sizer_left = wx.BoxSizer(wx.VERTICAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        sizer_left.Add(panel_clock, 0, wx.ALL, 5)
        sizer_left.Add(panel_calender, 0, wx.ALL | wx.ALIGN_TOP, 5)

        sizer_right.Add(panel_weather, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)
        sizer_right.Add(panel_sunset, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)
        sizer_right.Add(panel_vasttrafik, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)

        sizer_main.Add(sizer_left, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
        sizer_main.Add(sizer_right, 1, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 5)

        self.SetSizer(sizer_main)
        self.Fit()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tick, self.timer)
        self.timer.Start(500)

        self.Bind(wx.EVT_KEY_DOWN, self.on_keypress)

        self.Show()

    def tick(self, ev):
        now = datetime.now()

        if (now - self.vasttrafik.updated_graphics).seconds >= self.vasttrafik.update_freq_graphics:
            self.vasttrafik.update()

        if (now - self.vasttrafik.updated_data).seconds >= self.vasttrafik.update_freq_data:
            self.vasttrafik.updateDataSet()

        self.calender.update_check()
        self.weather.update_check()
        self.clock.update_check()

    def on_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE or keycode == wx.WXK_RETURN:
            print("you pressed the spacebar!")
            self.ShowFullScreen(True)
            event.Skip()
        elif keycode == wx.WXK_ESCAPE:
            print("you pressed the escape button!")
            self.ShowFullScreen(False)
            event.Skip()


app = wx.App()
Example(None, title='Magic Mirror')
app.MainLoop()
