

from datetime import datetime
from datetime import timedelta
import requests
import wx
import pytz


class ModuleSunriseSunset:
    timezone = pytz.timezone('Europe/Stockholm')
    fontSize = 25

    def __init__(self, panel_main, userSettings):
        self.panel_main = panel_main

        self.updateFreqData = userSettings['updateFreqData'] if 'updateFreqData' in userSettings else 600
        self.updateFreqGraphics = userSettings['updateFreqGraphics'] if 'updateFreqGraphics' in userSettings else 60
        print(userSettings)
        if 'places' in userSettings:
            place = next(iter(userSettings['places']))
        else:
            place = ''
        
        self.lat = userSettings['places'][place]['lat'] if 'lat' in userSettings['places'][place] else 64.75203
        self.long = userSettings['places'][place]['long'] if 'long' in userSettings['places'][place] else 64.75203
        
        self.url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}&formatted=0'.format(self.lat, self.long, datetime.now().strftime('%Y-%m-%d'))

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font1 = wx.Font(pointSize=self.fontSize, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
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

        sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        for i in range(2):
            sizerVert = wx.BoxSizer(wx.VERTICAL)
            tmpStr = self.sunrise.strftime("%H:%M") if i == 0 else self.sunset.strftime("%H:%M")
            lblNew = wx.StaticText(panel, label=tmpStr)
            lblNew.SetBackgroundColour('Black')
            lblNew.SetForegroundColour('White')
            lblNew.SetFont(self.font1)

            png = wx.Image("pics/sunrise3.png" if i == 0 else "pics/sunset3.png", wx.BITMAP_TYPE_ANY).Scale(64, 64, wx.IMAGE_QUALITY_HIGH)
            pic=wx.StaticBitmap(panel, -1, wx.Bitmap(png))

            sizerVert.Add(pic, 0, wx.ALIGN_CENTER)
            sizerVert.Add(lblNew, 0, wx.ALIGN_CENTER)
            sizerVert.SetMinSize(150, -1)
            sizerMain.Add(sizerVert, 0, wx.ALIGN_LEFT if i == 0 else wx.ALIGN_RIGHT)

        #sizer_main.Add(lbl_sunrise, 1, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT, 0)
        #sizer_main.Add(pic_sunrise, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_LEFT, 0)
        #sizer_main.Add(lbl_sunset, 1, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 0)
        #sizer_main.Add(pic_sunset, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 0)


        panel.SetSizer(sizerMain)

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

        sunrise_utc = datetime.strptime(tmp['results']['sunrise'][0:-3]+'00', '%Y-%m-%dT%H:%M:%S%z')
        sunset_utc = datetime.strptime(tmp['results']['sunset'][0:-3]+'00', '%Y-%m-%dT%H:%M:%S%z')
        self.sunrise = sunrise_utc.astimezone(self.timezone)
        self.sunset = sunset_utc.astimezone(self.timezone)
