# -*- coding: utf-8 -*-
import wx
from datetime import datetime
import ModuleClock, ModuleVastTrafik, ModuleWeather, ModuleSunriseSunset
from GoogleCalendar.GoogleCalendar import ModuleCalendar

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

        panel_calendar1 = wx.Panel(self)
        self.calendar1 = ModuleCalendar(panel_calendar1, userInput_googleCalendar, ShowUpdatedList = False)

        panel_calendar2 = wx.Panel(self)
        panel_calendar2.SetBackgroundColour("Green")
        self.calendar2 = ModuleCalendar(panel_calendar2, userInput_googleCalendar, ShowMainCalendar = False)

        panel_weather = wx.Panel(self)
        self.weather = ModuleWeather.ModuleWeather(panel_weather, userInput_SMHI)

        panel_sunset = wx.Panel(self)
        self.sunset = ModuleSunriseSunset.ModuleSunriseSunset(panel_sunset, userInput_sunriseSunset)

        sizer_left = wx.BoxSizer(wx.VERTICAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_right_bottom = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        sizer_left.Add(panel_clock, 0, wx.LEFT, 15)
        sizer_left.Add(panel_vasttrafik, 0, wx.LEFT, 15)
        sizer_left.Add(panel_sunset, 0, wx.LEFT|wx.EXPAND, 15)

        sizer_right.Add(panel_calendar1, 0, wx.ALIGN_LEFT, 5)
        sizer_right_bottom.Add(panel_weather, 0, wx.ALIGN_LEFT, 5)
        sizer_right_bottom.Add(panel_calendar2, 0, wx.ALIGN_RIGHT, 5)
        sizer_right.Add(sizer_right_bottom, 0, wx.EXPAND|wx.ALIGN_LEFT, 5)

        sizer_main.Add(sizer_left, 1, wx.ALIGN_LEFT, 5)
        sizer_main.Add(sizer_right, 1, wx.ALL, 5)

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

        self.calendar1.UpdateCheck()
        self.calendar2.UpdateCheck()
        self.weather.UpdateCheck()
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
