# -*- coding: utf-8 -*-
import wx
from datetime import datetime
import ModuleClock, ModuleVastTrafik, ModuleCalender, ModuleWeather, ModuleSunriseSunset
import json
# import os
# import psutil

with open('MagicMirrorSettings.json', encoding='utf-8') as data_file:
    userSettings = json.load(data_file)

userInput_placesList = userSettings['placesList']
userInput_googleCalendar = userSettings['googleCalendar']
userInput_SMHI = userSettings['SMHI']
userInput_vastTrafik = userSettings['vastTrafik']
userInput_sunriseSunset = userSettings['sunriseSunset']

# Append (but don't replace) missing information SMHI 'places' from 'placesList'
for place in userInput_SMHI['places']:
    if place in userInput_placesList:
        userInput_SMHI['places'][place] = {**userInput_placesList[place], **userInput_SMHI['places'][place]}

# Append (but don't replace) missing information sunrise 'places' from 'placesList'
for place in userInput_sunriseSunset['places']:
    if place in userInput_placesList:
        userInput_sunriseSunset['places'][place] = {**userInput_placesList[place], **userInput_sunriseSunset['places'][place]}



class Example(wx.Frame):
    def __init__(self, parent, title):
        self.lastcall = datetime.now()
        super(Example, self).__init__(parent, title=title, size=(900, 750))
        self.SetBackgroundColour('Black')

        panel_clock = wx.Panel(self)
        self.clock = ModuleClock.ModuleClock(panel_clock)

        panel_vasttrafik = wx.Panel(self)
        self.vasttrafik = ModuleVastTrafik.ModuleVastTrafik(panel_vasttrafik, userInput_vastTrafik)

        panel_calender = wx.Panel(self)
        self.calender = ModuleCalender.ModuleCalender(panel_calender, userInput_googleCalendar)

        panel_weather = wx.Panel(self)
        self.weather = ModuleWeather.ModuleWeather(panel_weather, userInput_SMHI)

        panel_sunset = wx.Panel(self)
        self.sunset = ModuleSunriseSunset.ModuleSunriseSunset(panel_sunset, userInput_sunriseSunset)

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
        self.ShowFullScreen(True)

    def tick(self, ev):
        now = datetime.now()

        if (now - self.vasttrafik.updated_graphics).seconds >= self.vasttrafik.updateFreqGraphics:
            self.vasttrafik.update()

        if (now - self.vasttrafik.updated_data).seconds >= self.vasttrafik.updateFreqData:
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
