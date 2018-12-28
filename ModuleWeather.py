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

    def __init__(self, panel_main, *args, **kwargs):
        self.panel_main = panel_main

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 60
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 600

        self.places = kwargs['places'] if 'places' in kwargs else {'Skellefteå': {'lat': 64.75203, 'long': 20.95350}}
        self.index = 0
        self.place_names = []
        for place in self.places:
            self.place_names.append(place)
        self.data = [None]*len(self.places)

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()

        self.status_ok = False

        self.font1 = wx.Font(pointSize=54, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.font2 = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.font3 = wx.Font(pointSize=12, family=wx.FONTFAMILY_MODERN, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)

        self.update_dataset()
        self.update()

    def __str__(self):
        tmp_str = ''
        for myobj in self.panel_main.GetChildren():
            tmp_str += str(myobj) + '\n'
            for subobj in myobj.GetChildren():
                tmp_str += '   ' + str(subobj) + '\n'

        return tmp_str

    def update_check(self):
        now = datetime.now()
        if (now - self.updated_data).total_seconds() > 600:
            self.update_dataset()

        if (now - self.updated_graphics).total_seconds() > self.places[self.place_names[self.index]]['duration']:
            self.index = self.index + 1 if self.index < len(self.places)-1 else 0
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

        now = datetime.now()

        lbl_city = wx.StaticText(panel, label=self.place_names[self.index])
        lbl_city.SetForegroundColour('White')
        lbl_city.SetFont(self.font2)

        temp_val = self.getParameter(self.data[self.index]['timeSeries'][0], 't')
        lbl_temperature = wx.StaticText(panel, label='{:>5}{}'.format(str(temp_val), chr(176)))
        lbl_temperature.SetBackgroundColour('Black')
        lbl_temperature.SetForegroundColour('White')
        lbl_temperature.SetFont(self.font1)

        wsymb2 = self.getParameter(self.data[self.index]['timeSeries'][0], 'Wsymb2')

        new_height = 120
        png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY)
        png = png.Scale(int(png.GetWidth()/png.GetHeight()*new_height), new_height, wx.IMAGE_QUALITY_HIGH)
        mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))

        sizer_left = wx.BoxSizer(wx.VERTICAL)
        sizer_upper_left = wx.BoxSizer(wx.HORIZONTAL)

        sizer_upper_left.Add(lbl_temperature, 3, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_upper_left.Add(mypic, 2, wx.ALL, 0)

        # Data table for weather today
        n_div = 5
        delta_hour = int((24 - round(now.hour + 0.99)) / n_div + 0.99)
        sizer_table1 = wx.FlexGridSizer(n_div, 2, 0, 0)
        for i in range(1,n_div+1):
            curr_time = (now + timedelta(hours=i*delta_hour)).astimezone(self.timezone)
            time_serie = self.getTime(curr_time)
            valid_time = datetime.strptime(time_serie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            time_hour = valid_time.astimezone(self.timezone).hour
            temperature = self.getParameter(time_serie, 't')   # temperature degC
            pmean = self.getParameter(time_serie, 'pmean')     # Mean precipitation intensity mm/hour
            wsymb2 = self.getParameter(time_serie, 'Wsymb2')    # Weather symbol   1-27 integer

            lbl_1 = wx.StaticText(panel, label='kl.{:2}   {:>5}{}C    {:>4} mm/h'.format(time_hour, temperature,
                                                                                         chr(176), pmean))
            lbl_1.SetForegroundColour("White")
            lbl_1.SetFont(self.font3)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizer_table1.Add(lbl_1, 1, wx.ALIGN_CENTER_VERTICAL, 0)
            sizer_table1.Add(mypic, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

        sizer_table1.AddGrowableCol(1, 1)

        line1 = wx.StaticLine(panel, 0, style=wx.LI_HORIZONTAL)
        line1.SetForegroundColour('Grey')

        # Data table for weather tomorrow
        time_values = [0, 3, 6, 9, 12, 15, 18, 21, 24]
        sizer_table2 = wx.FlexGridSizer(len(time_values), 2, 2, 2)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        for time_value in time_values:
            curr_time = (tomorrow + timedelta(hours=time_value)).astimezone(self.timezone)
            time_serie = self.getTime(curr_time)
            valid_time = datetime.strptime(time_serie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            time_hour = valid_time.astimezone(self.timezone).hour
            temperature = self.getParameter(time_serie, 't')  # temperature degC
            pmean = self.getParameter(time_serie, 'pmean')  # Mean precipitation intensity mm/hour
            wsymb2 = self.getParameter(time_serie, 'Wsymb2')  # Weather symbol   1-27 integer

            lbl_1 = wx.StaticText(panel, label='kl.{:2}   {:>5}{}C    {:>4} mm/h'.format(time_hour, temperature,
                                                                                         chr(176), pmean))
            lbl_1.SetForegroundColour("White")
            lbl_1.SetFont(self.font3)
            png = wx.Image('pics/{}.png'.format(wsymb2), wx.BITMAP_TYPE_ANY).Scale(35, 24, wx.IMAGE_QUALITY_HIGH)
            mypic = wx.StaticBitmap(panel, -1, wx.Bitmap(png))
            sizer_table2.Add(lbl_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
            sizer_table2.Add(mypic, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

        sizer_table2.AddGrowableCol(1, 1)

        sizer_left.Add(lbl_city, 0, wx.ALIGN_CENTER, 0)
        sizer_left.Add(sizer_upper_left, 0, wx.EXPAND, 0)
        sizer_left.Add(sizer_table1, 0, wx.EXPAND, 0)
        sizer_left.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_left.Add(sizer_table2, 0, wx.EXPAND, 0)

        panel.SetSizer(sizer_left)

        panel.Fit()
        self.panel_main.Fit()

        panel.Thaw()
        self.panel_main.Thaw()

    def update_dataset(self):
        """
        Updates the data set from SMHI weather service

        """

        cnt = -1
        for place_name, place in self.places.items():
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
            if self.status_ok is True:
                self.data[cnt] = tmp

    def getCurrentWeather(self):
        """
        Get time_serie
        """
        now = datetime.now(self.timezone)

        for time_serie in self.data[self.index]['timeSeries']:
            curr_time = datetime.strptime(time_serie['validTime'], '%Y-%m-%dT%H:%M:%S%z')
            if (curr_time - now).total_seconds() < 3600:
                return time_serie

    def getParameter(self, time_serie, parameter_name):
        """
        Returns the value of the specified parameter (parameter_name) for a specified time_serie given in
        the SMHI format
        """
        requested_parameter = next((item for item in time_serie['parameters'] if item['name'] == parameter_name), None)
        return requested_parameter['values'][0]

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
