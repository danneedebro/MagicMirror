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
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json'
    timezone = pytz.timezone('Europe/Stockholm')
    weather_symb = {1: "Klart", 2: "Lätt molnighet", 3: "Halvklart", 4: "Molnigt", 5: "Mycket moln", 6: "Mulet",
                    7: "Dimma", 8: "Lätt regnskur", 9: "Regnskur", 10: "Kraftig regnskur", 11: "Åskskur",
                    12: "Lätt by av regn och snö", 13: "By av regn och snö", 14: "Kraftig by av regn och snö",
                    15: "Lätt snöby", 16: "Snöby", 17: "Kraftig snöby", 18: "Lätt regn", 19: "Regn",
                    20: "Kraftigt regn", 21: "Åska", 22: "Lätt snöblandat regn", 23: "Snöblandat regn",
                    24: "Kraftigt snöblandat regn", 25: "Lätt snöfall", 26: "Snöfall", 27: "Ymnigt snöfall"}

    def __init__(self, mainPanel, *args, **kwargs):
        self.mainPanel = mainPanel

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 60
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 600

        self.places = kwargs['places'] if 'places' in kwargs else {'Skellefteå': {'lat': 64.75203, 'long': 20.95350}}
        self.index = 2
        self.place_names = []
        for place in self.places:
            self.place_names.append(place)
        self.data = [None]*len(self.places)

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

    def do_update(self):
        if (datetime.now() - self.updated_graphics).total_seconds() > 10:
            print('UPPDATERAR {}'.format(self.index))
            self.index = self.index + 1 if self.index < len(self.places)-1 else 0
            print('UPPDATERAR {}'.format(self.index))
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

        LblCity = wx.StaticText(panel, label=self.place_names[self.index])
        LblCity.SetForegroundColour('White')
        LblCity.SetFont(self.font_other)

        tempVal = self.getParameter(self.data[self.index]['timeSeries'][0], 't')
        LblTemperature = wx.StaticText(panel, label='{:>5}{}'.format(str(tempVal), chr(176)))
        LblTemperature.SetBackgroundColour('Black')
        LblTemperature.SetForegroundColour('White')
        LblTemperature.SetFont(self.font_temp)

        wsymb2 = self.getParameter(self.data[self.index]['timeSeries'][0], 'Wsymb2')

        new_height = 120
        png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY)
        png = png.Scale(int(png.GetWidth()/png.GetHeight()*new_height), new_height, wx.IMAGE_QUALITY_HIGH)
        mypic=wx.StaticBitmap(panel, -1, wx.Bitmap(png))



        sizerMain = wx.BoxSizer(wx.HORIZONTAL)
        sizerLeft = wx.BoxSizer(wx.VERTICAL)
        sizerUpperLeft = wx.BoxSizer(wx.HORIZONTAL)

        sizerUpperLeft.Add(LblTemperature, 3, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizerUpperLeft.Add(mypic, 2, wx.ALL, 0)



        # Data table for weather today
        nDiv = 5
        delta_hour = int((24 - round(now.hour + 0.99)) / nDiv + 0.99)
        sizerTable1 = wx.FlexGridSizer(nDiv, 2, 0, 0)
        for i in range(1,nDiv+1):
            cTime = (now + timedelta(hours=i*delta_hour)).astimezone(self.timezone)
            timeSerie = self.getTime(cTime)
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            time_hour = validtime.astimezone(self.timezone).hour
            temperature = self.getParameter(timeSerie, 't')   # temperature degC
            pmean = self.getParameter(timeSerie, 'pmean')     # Mean precipitation intensity mm/hour
            wsymb2 = self.getParameter(timeSerie, 'Wsymb2')    # Weather symbol   1-27 integer

            Lbl1 = wx.StaticText(panel, label='kl.{:2}   {:>5}{}C    {:>4} mm/h'.format(time_hour, temperature, chr(176), pmean))
            Lbl1.SetForegroundColour("White")
            Lbl1.SetFont(self.font_table)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizerTable1.Add(Lbl1, 1, wx.ALIGN_CENTER_VERTICAL, 0)
            sizerTable1.Add(mypic, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

            print('Kl {} {}:  T={}{}   {}'.format(validtime.astimezone(self.timezone).hour, timeSerie['validTime'], self.getParameter(timeSerie, 't'), chr(176), timeSerie))

        sizerTable1.AddGrowableCol(1, 1)

        line1 = wx.StaticLine(panel, 0, style=wx.LI_HORIZONTAL)
        line1.SetForegroundColour('Grey')


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
                                 label='kl.{:2}   {:>5}{}C    {:>4} mm/h'.format(time_hour, temperature, chr(176), pmean))
            Lbl1.SetForegroundColour("White")
            Lbl1.SetFont(self.font_table)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizerTable2.Add(Lbl1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizerTable2.Add(mypic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

            print('Kl {} {}:  T={}{}   {}'.format(validtime.astimezone(self.timezone).hour, timeSerie['validTime'],
                                                  self.getParameter(timeSerie, 't'), chr(176), timeSerie))

        sizerTable2.AddGrowableCol(1, 1)


        sizerLeft.Add(LblCity, 0, wx.ALIGN_CENTER, 0)
        sizerLeft.Add(sizerUpperLeft, 0, wx.EXPAND, 0)
        sizerLeft.Add(sizerTable1, 0, wx.EXPAND, 0)
        sizerLeft.Add(line1, 0, wx.ALL|wx.EXPAND, 5)
        sizerLeft.Add(sizerTable2, 0, wx.EXPAND, 0)

        panel.SetSizer(sizerLeft)

        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()
        self.mainPanel.Thaw()


    def updateDataSet(self):
        """
        Updates the data set from SMHI weather service

        """

        cnt = -1
        for place_name, place in self.places.items():
            print(place_name)
            print(place)
            cnt += 1

            print('Retrieving data from SMHI\n   lat={}, long={}'.format(place['lat'], place['long']))
            self.updated_data = datetime.now()

            url = self.url.format(place['long'], place['lat'])

            r = requests.get(url)

            if r.status_code == 200:
                tmp = r.json()
                self.status_ok = True
            else:
                print('Error during GET request to SMHI' + str(r.status_code) + str(r.content) + ', url=' + r.url)
                self.status_ok = False

            # If data retrieved OK, load it into self.data
            if self.status_ok == True:
                self.data[cnt] = tmp

    def getCurrentWeather(self):
        """
        Get timeSerie
        """
        now = datetime.now(self.timezone)

        for timeSerie in self.data[self.index]['timeSeries']:
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
        validtime_prev = datetime.strptime(self.data[self.index]['referenceTime'], '%Y-%m-%dT%H:%M:%S%z')
        for timeSerie in self.data[self.index]['timeSeries']:
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if validtime_prev < local_datetime <= validtime:
                return timeSerie

    def getTimeAverage(self, startTime, endTime, param_str):
        values = []
        for timeSerie in self.data[self.index]['timeSeries']:
            validtime = datetime.strptime(timeSerie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if startTime < validtime <= endTime:
                for parameter in timeSerie['parameters']:
                    if parameter['name'] == param_str:
                        values.append(parameter['values'][0])
                print('Valid time is {}   {}'.format(timeSerie['validTime'], startTime))

        print(values)