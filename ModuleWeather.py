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
        self.timezone = pytz.timezone('Europe/Stockholm')

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font_temp = wx.Font(pointSize=54, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
                                     weight=wx.FONTWEIGHT_NORMAL)
        self.font_other = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                                   weight=wx.FONTWEIGHT_NORMAL)
        self.font_table = wx.Font(pointSize=12, family=wx.FONTFAMILY_MODERN, style=wx.NORMAL,
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

        png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(172, 120, wx.IMAGE_QUALITY_HIGH)
        mypic=wx.StaticBitmap(panel, -1, wx.Bitmap(png))

        line1 = wx.StaticLine(panel, 0, style=wx.LI_VERTICAL)
        line1.SetForegroundColour('White')

        sizerMain = wx.BoxSizer(wx.HORIZONTAL)
        sizerLeft = wx.BoxSizer(wx.VERTICAL)
        sizerUpperLeft = wx.BoxSizer(wx.HORIZONTAL)

        sizerUpperLeft.Add(LblTemperature, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        #sizerMain.Add(LblTypeOfWeather, 0, wx.ALIGN_RIGHT, 0)
        sizerUpperLeft.Add(mypic, 0, wx.ALL, 0)



        # Data table for weather today
        nDiv = 5
        delta_hour = int((24 - round(now.hour + 0.99)) / nDiv + 0.99)
        sizerTable1 = wx.FlexGridSizer(nDiv, 2, 2, 2)
        for i in range(1,nDiv+1):
            cTime = (now + timedelta(hours=i*delta_hour)).astimezone(self.timezone)
            timeSerie = self.getTime(cTime)
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            time_hour = validtime.astimezone(self.timezone).hour
            temperature = self.getParameter(timeSerie, 't')   # temperature degC
            pmean = self.getParameter(timeSerie, 'pmean')     # Mean precipitation intensity mm/hour
            wsymb2 = self.getParameter(timeSerie, 'Wsymb2')    # Weather symbol   1-27 integer

            Lbl1 = wx.StaticText(panel, label='kl.{:2}   {}{}C    {} mm/h'.format(time_hour, temperature, chr(176), pmean))
            Lbl1.SetForegroundColour("White")
            Lbl1.SetFont(self.font_table)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizerTable1.Add(Lbl1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizerTable1.Add(mypic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

            print('Kl {} {}:  T={}{}   {}'.format(validtime.astimezone(self.timezone).hour, timeSerie['validTime'], self.getParameter(timeSerie, 't'), chr(176), timeSerie))

        sizerTable1.AddGrowableCol(1, 2)

        # Data table for weather tomorrow
        time_values = [0, 3, 6, 9, 12, 15, 18, 21, 24]
        sizerTable2 = wx.FlexGridSizer(len(time_values), 2, 2, 2)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        for time_value in time_values:
            cTime = (tomorrow + timedelta(hours=time_value)).astimezone(self.timezone)
            timeSerie = self.getTime(cTime)
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            time_hour = validtime.astimezone(self.timezone).hour
            temperature = self.getParameter(timeSerie, 't')  # temperature degC
            pmean = self.getParameter(timeSerie, 'pmean')  # Mean precipitation intensity mm/hour
            wsymb2 = self.getParameter(timeSerie, 'Wsymb2')  # Weather symbol   1-27 integer

            Lbl1 = wx.StaticText(panel,
                                 label='kl.{:2}   {}{}C    {} mm/h'.format(time_hour, temperature, chr(176), pmean))
            Lbl1.SetForegroundColour("White")
            Lbl1.SetFont(self.font_table)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizerTable2.Add(Lbl1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizerTable2.Add(mypic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

            print('Kl {} {}:  T={}{}   {}'.format(validtime.astimezone(self.timezone).hour, timeSerie['validTime'],
                                                  self.getParameter(timeSerie, 't'), chr(176), timeSerie))

        sizerTable2.AddGrowableCol(1, 2)



        sizerLeft.Add(sizerUpperLeft, 0, wx.EXPAND, 0)
        sizerLeft.Add(sizerTable1, 0, wx.EXPAND, 0)

        sizerMain.Add(sizerLeft)
        sizerMain.Add(line1, 0, wx.ALL | wx.EXPAND, 0)
        sizerMain.Add(sizerTable2)

        panel.SetSizer(sizerMain)

        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()
        self.mainPanel.Thaw()


    def updateDataSet(self):
        """
        Updates the data set from SMHI weather service

        """
        print('Retrieving data from SMHI\n   lat={}, long={}'.format(self.lat, self.long))
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

    def getTime(self, local_datetime):
        validtime_prev = datetime.strptime(self.data['referenceTime'], '%Y-%m-%dT%H:%M:%S%z')
        for timeSerie in self.data['timeSeries']:
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if validtime_prev < local_datetime <= validtime:
                return timeSerie

    def getTimeAverage(self, startTime, endTime, param_str):
        values = []
        for timeSerie in self.data['timeSeries']:
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if startTime < validtime <= endTime:
                for parameter in timeSerie['parameters']:
                    if parameter['name'] == param_str:
                        values.append(parameter['values'][0])
                print('Valid time is {}   {}'.format(timeSerie['validTime'], startTime))

        print(values)