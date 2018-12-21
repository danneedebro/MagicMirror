

from datetime import datetime
from datetime import timedelta
import requests
import wx
import pytz


class ModuleSunriseSunset:
    def __init__(self, mainPanel, *args, **kwargs):
        self.mainPanel = mainPanel

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 60
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 600

        self.lat = kwargs['lat'] if 'lat' in kwargs else 64.75203
        self.long = kwargs['long'] if 'long' in kwargs else 20.95350
        self.url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}&formatted=0'.format(self.lat, self.long, datetime.now().strftime('%Y-%m-%d'))

        fontSize = kwargs['fontSize'] if 'fontSize' in kwargs else 25

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font_temp = wx.Font(pointSize=fontSize, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
                                     weight=wx.FONTWEIGHT_NORMAL)
        self.font_other = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                                   weight=wx.FONTWEIGHT_NORMAL)

        self.updateDataSet()
        self.update()

    def update(self):
        now = datetime.now()
        self.updated_graphics = now

        self.mainPanel.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.mainPanel)
        panel.SetBackgroundColour('Black')
        panel.Freeze()  # Freeze to avoid flickering

        LblSunrise = wx.StaticText(panel, label=self.sunrise.strftime('%H:%M'))
        LblSunrise.SetBackgroundColour('Black')
        LblSunrise.SetForegroundColour('White')
        LblSunrise.SetFont(self.font_temp)

        LblSunset = wx.StaticText(panel, label=self.sunset.strftime('  %H:%M'))
        LblSunset.SetBackgroundColour('Black')
        LblSunset.SetForegroundColour('White')
        LblSunset.SetFont(self.font_temp)

        pngSunrise = wx.Image('pics/sunrise3.png', wx.BITMAP_TYPE_ANY).Scale(64, 64, wx.IMAGE_QUALITY_HIGH)
        picSunrise=wx.StaticBitmap(panel, -1, wx.Bitmap(pngSunrise))

        pngSunset = wx.Image('pics/sunset3.png', wx.BITMAP_TYPE_ANY).Scale(64, 64, wx.IMAGE_QUALITY_HIGH)
        picSunset = wx.StaticBitmap(panel, -1, wx.Bitmap(pngSunset))  # , size=(png.GetWidth(), png.GetHeight()))

        sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        sizerMain.Add(LblSunrise, 0, wx.ALL|wx.ALIGN_BOTTOM, 0)
        sizerMain.Add(picSunrise, 0, wx.ALL|wx.ALIGN_BOTTOM, 0)
        sizerMain.Add(LblSunset, 0, wx.ALL|wx.ALIGN_BOTTOM, 0)
        sizerMain.Add(picSunset, 0, wx.ALL|wx.ALIGN_BOTTOM, 0)


        panel.SetSizer(sizerMain)

        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()
        self.mainPanel.Thaw()


    def updateDataSet(self):
        """
        Updates the data set from SMHI weather service

        """
        print('Retrieving data from sunrise-sunset.org\n   lat={}, long={}'.format(self.lat, self.long))
        self.updated_data = datetime.now()
        self.url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}&formatted=0'.format(self.lat, self.long, datetime.now().strftime('%Y-%m-%d'))
        r = requests.get(self.url)

        if r.status_code == 200:
            tmp = r.json()
            self.status_ok = True
        else:
            print('Error during GET request to SMHI' + str(r.status_code) + str(r.content))
            self.status_ok = False

        sunrise_utc = datetime.strptime(tmp['results']['sunrise'], '%Y-%m-%dT%H:%M:%S%z')
        sunset_utc = datetime.strptime(tmp['results']['sunset'], '%Y-%m-%dT%H:%M:%S%z')
        self.sunrise = sunrise_utc.astimezone(pytz.timezone('Europe/Stockholm'))
        self.sunset = sunset_utc.astimezone(pytz.timezone('Europe/Stockholm'))
