#   -----------------------------
#   |DATE         |         WEEK|
#   -----------------------------
#   |           TIME            |
#   |                           |
#   -----------------------------


from datetime import datetime
from datetime import timedelta
import requests
import wx
import pytz


class ModuleWeather:
    def __init__(self, mainPanel, *args, **kwargs):
        self.mainPanel = mainPanel

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 60
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 600

        self.lat = kwargs['lat'] if 'lat' in kwargs else 64.75203
        self.long = kwargs['long'] if 'long' in kwargs else 20.95350
        self.url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json'.format(self.long, self.lat)

        self.weather_symb = {1: "Klart", 2: "Lätt molnighet", 3: "Halvklart", 4: "Molnigt", 5: "Mycket moln", 6: "Mulet", 7: "Dimma", 8: "Lätt regnskur", 9: "Regnskur", 10: "Kraftig regnskur", 11: "Åskskur", 12: "Lätt by av regn och snö", 13: "By av regn och snö", 14: "Kraftig by av regn och snö", 15: "Lätt snöby", 16: "Snöby", 17: "Kraftig snöby", 18: "Lätt regn", 19: "Regn", 20: "Kraftigt regn", 21: "Åska", 22: "Lätt snöblandat regn", 23: "Snöblandat regn", 24: "Kraftigt snöblandat regn", 25: "Lätt snöfall", 26: "Snöfall", 27: "Ymnigt snöfall"}

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font_temp = wx.Font(pointSize=54, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
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

        now = datetime.now()
        tempVal = self.getParameter(self.data['timeSeries'][0], 't')
        LblTemperature = wx.StaticText(panel, label=str(tempVal) + chr(176))
        LblTemperature.SetBackgroundColour('Black')
        LblTemperature.SetForegroundColour('White')
        LblTemperature.SetFont(self.font_temp)

        wsymb2 = self.getParameter(self.data['timeSeries'][0], 'Wsymb2')
        #LblTypeOfWeather = wx.StaticText(panel, label=self.weather_symb[wsymb2])#, style=wx.ALIGN_RIGHT)
        #LblTypeOfWeather.SetBackgroundColour('Black')
        #LblTypeOfWeather.SetForegroundColour('White')
        #LblTypeOfWeather.SetFont(self.font_other)

        png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(120, 120, wx.IMAGE_QUALITY_HIGH)
        mypic=wx.StaticBitmap(panel, -1, wx.Bitmap(png))#, size=(png.GetWidth(), png.GetHeight()))

        sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        sizerMain.Add(LblTemperature, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        #sizerMain.Add(LblTypeOfWeather, 0, wx.ALIGN_RIGHT, 0)
        sizerMain.Add(mypic, 0, wx.ALL, 0)

        panel.SetSizer(sizerMain)

        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()
        self.mainPanel.Thaw()


    def updateDataSet(self):
        """
        Updates the data set from SMHI weather service

        """
        print('Retrieving data from SMHI')
        self.updated_data = datetime.now()

        r = requests.get(self.url)

        if r.status_code == 200:
            tmp = r.json()
            self.status_ok = True
        else:
            print('Error during GET request to SMHI' + str(r.status_code) + str(r.content))
            self.status_ok = False

        # If data retrieved OK, load it into self.data
        if self.status_ok == True:
            self.data = tmp

    def getCurrentWeather(self):
        """
        Get timeSerie
        """
        now = datetime.now(pytz.timezone('Europe/Stockholm'))

        for timeSerie in self.data['timeSeries']:
            currTime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if (currTime - now).total_seconds() < 3600:
                return timeSerie



    def getParameter(self, timeSerie, strParam):
        """
        Returns the value of the specified parameter (strParam) for a specified timeSerie given in
        the SMHI format
        """
        requestedParameter = next((item for item in timeSerie['parameters'] if item['name'] == strParam), None)
        return requestedParameter['values'][0]