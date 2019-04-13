# -*- coding: utf-8 -*-
import wx
from datetime import datetime
import logging
import json

from ModuleClock import ModuleClock
from ModuleVastTrafik import ModuleVastTrafik
from ModuleWeather import ModuleWeather
from ModuleSunriseSunset import ModuleSunriseSunset
from GoogleCalendar.GoogleCalendar import ModuleCalendar

# Initialize logger
LOG_FORMAT = "\n%(levelname)s: in %(module)s (%(funcName)s), %(asctime)s - %(message)s"
logging.basicConfig(filename = "ErrorLog.txt", level=logging.CRITICAL, format=LOG_FORMAT, filemode = 'w')
logger = logging.getLogger("MagicMirror")
logger.setLevel(logging.DEBUG)

logger.info("Program started")
logger.info("Reading settings")
try:
    with open('MagicMirrorSettings.json', encoding='utf-8') as data_file:
        userSettings = json.load(data_file)
except Exception as e:
    logger.critical("Error reading settings json: {}".format(e))
    raise


userInput_placesList = userSettings['placesList'] if 'placesList' in userSettings else {}
userInput_googleCalendar = userSettings['googleCalendar'] if 'googleCalendar' in userSettings else {}
userInput_SMHI = userSettings['SMHI'] if 'SMHI' in userSettings else {}
userInput_vastTrafik = userSettings['vastTrafik'] if 'vastTrafik' in userSettings else {}
userInput_sunriseSunset = userSettings['sunriseSunset'] if 'sunriseSunset' in userSettings else {}

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

        #panel_clock = wx.Panel(self)
        self.clock = ModuleClock(self)
        self.clock.SetBackgroundColour("Green")

        self.vasttrafik = ModuleVastTrafik(self, userInput_vastTrafik)

        self.calendar1 = ModuleCalendar(self, userInput_googleCalendar, ShowUpdatedList = False)

        self.calendar2 = ModuleCalendar(self, userInput_googleCalendar, ShowMainCalendar = False)

        self.weather = ModuleWeather(self, userInput_SMHI)

        self.sunset = ModuleSunriseSunset(self, userInput_sunriseSunset)

        sizer_left = wx.BoxSizer(wx.VERTICAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_right_bottom = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        sizer_calendar2 = wx.BoxSizer(wx.VERTICAL)

        sizer_left.Add(self.clock, 0, wx.LEFT, 15)
        sizer_left.Add(self.vasttrafik, 0, wx.LEFT, 15)
        sizer_left.Add(self.sunset, 0, wx.LEFT|wx.EXPAND, 15)

        sizer_right.Add(self.calendar1, 0, wx.ALIGN_LEFT, 5)
        sizer_right_bottom.Add(self.weather, 1, wx.ALIGN_LEFT|wx.TOP, 25)
        sizer_calendar2.Add(self.calendar2, 0, wx.ALIGN_RIGHT)
        sizer_right_bottom.Add(sizer_calendar2, 1, wx.ALIGN_RIGHT, 5)
        sizer_right.Add(sizer_right_bottom, 0, wx.EXPAND|wx.ALIGN_LEFT, 5)

        sizer_main.Add(sizer_left, 1, wx.ALIGN_LEFT, 5)
        sizer_main.Add(sizer_right, 1, wx.ALL, 5)

        self.SetSizer(sizer_main)
        self.UpdatedComplete = datetime.now()
        self.Fit()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tick, self.timer)
        self.timer.Start(500)

        self.Bind(wx.EVT_KEY_DOWN, self.on_keypress)

        self.Show()
        self.ShowFullScreen(True)

    def tick(self, ev):
        now = datetime.now()

        self.vasttrafik.UpdateCheck()
        self.calendar1.UpdateCheck()
        self.calendar2.UpdateCheck()
        self.weather.UpdateCheck()
        self.clock.UpdateCheck()
        
        if (now - self.UpdatedComplete).seconds > 120:
            self.UpdatedComplete = datetime.now()
            self.Refresh()
        

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
