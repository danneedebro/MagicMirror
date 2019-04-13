from datetime import datetime
from datetime import timedelta
import requests
import wx
import pytz
from ModuleBase import ModuleBase

class ModuleSunriseSunset(ModuleBase):
    timezone = pytz.timezone('Europe/Stockholm')
    fontSize = 25

    def __init__(self, parent, userSettings):
        super().__init__(parent, **userSettings)

        print(userSettings)
        if 'places' in userSettings:
            place = next(iter(userSettings['places']))
        else:
            place = ''
        
        self.lat = userSettings['places'][place]['lat'] if 'lat' in userSettings['places'][place] else 64.75203
        self.long = userSettings['places'][place]['long'] if 'long' in userSettings['places'][place] else 64.75203
        
        self.url = 'https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}&formatted=0'.format(self.lat, self.long, datetime.now().strftime('%Y-%m-%d'))

        self.status_ok = False

        self.font1 = wx.Font(pointSize=self.fontSize, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
                             weight=wx.FONTWEIGHT_NORMAL)
        self.font2 = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL)

        self.UpdateCheck(updateDataNow = True, updateGraphisNow = True)

    def UpdateGraphics(self):
        super().UpdateGraphics()
        
        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self)
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

        panel.SetSizer(sizerMain)

        panel.Fit()
        self.Fit()

        panel.Thaw()
        self.Thaw()

    def UpdateData(self):
        """
        Updates the data set from SMHI weather service

        """
        super().UpdateData()
        
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
