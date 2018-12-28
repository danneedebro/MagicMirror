

from datetime import datetime
from datetime import timedelta
import requests
import wx
import pytz


class ModuleSunriseSunset:
    timezone = pytz.timezone('Europe/Stockholm')

    def __init__(self, panel_main, *args, **kwargs):
        self.panel_main = panel_main

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 60
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 600

        self.lat = kwargs['lat'] if 'lat' in kwargs else 64.75203
        self.long = kwargs['long'] if 'long' in kwargs else 20.95350
        self.url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}&formatted=0'.format(self.lat, self.long, datetime.now().strftime('%Y-%m-%d'))

        font_size = kwargs['font_size'] if 'font_size' in kwargs else 25

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font1 = wx.Font(pointSize=font_size, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
                             weight=wx.FONTWEIGHT_NORMAL)
        self.font2 = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL)

        self.update_dataset()
        self.update()

    def update(self):
        now = datetime.now()
        self.updated_graphics = now

        self.panel_main.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.panel_main.GetChildren():
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.panel_main)
        panel.SetBackgroundColour('Black')
        panel.Freeze()  # Freeze to avoid flickering

        lbl_sunrise = wx.StaticText(panel, label=self.sunrise.strftime('%H:%M'))
        lbl_sunrise.SetBackgroundColour('Black')
        lbl_sunrise.SetForegroundColour('White')
        lbl_sunrise.SetFont(self.font1)

        lbl_sunset = wx.StaticText(panel, label=self.sunset.strftime('  %H:%M'))
        lbl_sunset.SetBackgroundColour('Black')
        lbl_sunset.SetForegroundColour('White')
        lbl_sunset.SetFont(self.font1)

        png_sunrise = wx.Image('pics/sunrise3.png', wx.BITMAP_TYPE_ANY).Scale(64, 64, wx.IMAGE_QUALITY_HIGH)
        pic_sunrise=wx.StaticBitmap(panel, -1, wx.Bitmap(png_sunrise))

        png_sunset = wx.Image('pics/sunset3.png', wx.BITMAP_TYPE_ANY).Scale(64, 64, wx.IMAGE_QUALITY_HIGH)
        pic_sunset = wx.StaticBitmap(panel, -1, wx.Bitmap(png_sunset))  # , size=(png.GetWidth(), png.GetHeight()))

        sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        sizer_main.Add(lbl_sunrise, 1, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT, 0)
        sizer_main.Add(pic_sunrise, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT, 0)
        sizer_main.Add(lbl_sunset, 1, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 0)
        sizer_main.Add(pic_sunset, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 0)


        panel.SetSizer(sizer_main)

        panel.Fit()
        self.panel_main.Fit()

        panel.Thaw()
        self.panel_main.Thaw()

    def update_dataset(self):
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
        self.sunrise = sunrise_utc.astimezone(self.timezone)
        self.sunset = sunset_utc.astimezone(self.timezone)
