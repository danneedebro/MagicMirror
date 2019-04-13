from datetime import datetime
from datetime import timedelta
import requests
import wx
import wx.lib.stattext as ST
import pytz
from ModuleBase import ModuleBase

import json   # REMOVE

class ModuleWeather(ModuleBase):
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json'
    timezone = pytz.timezone('Europe/Stockholm')
    weather_symb = {1: "Klart", 2: "Lätt molnighet", 3: "Halvklart", 4: "Molnigt", 5: "Mycket moln", 6: "Mulet",
                    7: "Dimma", 8: "Lätt regnskur", 9: "Regnskur", 10: "Kraftig regnskur", 11: "Åskskur",
                    12: "Lätt by av regn och snö", 13: "By av regn och snö", 14: "Kraftig by av regn och snö",
                    15: "Lätt snöby", 16: "Snöby", 17: "Kraftig snöby", 18: "Lätt regn", 19: "Regn",
                    20: "Kraftigt regn", 21: "Åska", 22: "Lätt snöblandat regn", 23: "Snöblandat regn",
                    24: "Kraftigt snöblandat regn", 25: "Lätt snöfall", 26: "Snöfall", 27: "Ymnigt snöfall"}

    def __init__(self, parent, userSettings):
        super().__init__(parent, **userSettings)

        self.places = userSettings['places'] if 'places' in userSettings else {'Skellefteå': {'lat': 64.75203, 'long': 20.95350}}
        
        self.Weather = GetSMHIWeather(userSettings)
        self.UpdateData()
        
        self.UpdateGraphics()

    def UpdateData(self):
        super().UpdateData()
        self.Weather.GetWeather()

    def UpdateGraphics(self):
        super().UpdateGraphics()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self)
        panel.SetBackgroundColour('Black')

        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())

        sizerMain = wx.BoxSizer(wx.HORIZONTAL)

        weatherCurr = self.Weather.GetMedianWeather("Göteborg", Now, 1)
        symb = weatherCurr["Wsymb2"]["values"][0]
        Tmin, Tmax = (None, weatherCurr["t"]["values"][0])
        pmean, pmax = (weatherCurr["pmean"]["values"][0], weatherCurr["pmax"]["values"][0])
        wsMin, wsMax = (None, weatherCurr["ws"]["values"][0])
        weatherBoxNew = WeatherBox(panel, "Nu", symb, Tmin, Tmax, pmean, pmax, wsMin, wsMax, 0, 0, 3, 7)
        sizerMain.Add(weatherBoxNew, 0, wx.ALL, 3)

        weatherNext8h = self.Weather.GetMedianWeather("Göteborg", Now, 8)
        symb = round(sum(weatherNext8h["Wsymb2"]["values"])/len(weatherNext8h["Wsymb2"]["values"]))
        Tmin, Tmax = (min(weatherNext8h["t"]["values"]), max(weatherNext8h["t"]["values"]))
        pmean, pmax = (sum(weatherNext8h["pmean"]["values"]), max(weatherNext8h["pmax"]["values"]))
        wsMin, wsMax = (min(weatherNext8h["ws"]["values"]), max(weatherNext8h["ws"]["values"]))
        weatherBoxNew = WeatherBox(panel, "Nästa 8h", symb, Tmin, Tmax, pmean, pmax, wsMin, wsMax, 0, 0, 3, 7)
        sizerMain.Add(weatherBoxNew, 0, wx.ALL, 3)

        dateTomorrow = (Now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        weatherTomorrow = self.Weather.GetMedianWeather("Göteborg", dateTomorrow, 6)
        symb = round(sum(weatherTomorrow["Wsymb2"]["values"])/len(weatherTomorrow["Wsymb2"]["values"]))
        Tmin, Tmax = (min(weatherTomorrow["t"]["values"]), max(weatherTomorrow["t"]["values"]))
        pmean, pmax = (sum(weatherTomorrow["pmean"]["values"]), max(weatherTomorrow["pmax"]["values"]))
        wsMin, wsMax = (min(weatherTomorrow["ws"]["values"]), max(weatherTomorrow["ws"]["values"]))
        weatherBoxNew = WeatherBox(panel, "Imorgon 9-15", symb, Tmin, Tmax, pmean, pmax, wsMin, wsMax, 0, 0, 3, 7)
        sizerMain.Add(weatherBoxNew, 0, wx.ALL, 3)

        panel.SetSizerAndFit(sizerMain)
        self.Thaw()



class WeatherBox(wx.Panel):
    ImageHeight = 80
    FontSizeTemp = 54
    FontSizeOther = 14
    def __init__(self, Parent, Header, Symbol, TemperatureMin, TemperatureMax, Precipitation, PrecipitationMax, WindspeedMin, \
               WindSpeedMax, WindDirection1, WindDirection2, WindGustMin, WindGustMax):
        wx.Panel.__init__(self, Parent, -1)
        self.SetBackgroundColour("Black")
        self.sizerMain = wx.BoxSizer(wx.VERTICAL)

        Fields = dict()
        Fields["1. Header"] = {"Text": Header, "FontSize": 12}
        Fields["2. Temperature"] = {"Text": "{}{}C".format(TemperatureMax if TemperatureMin is None else "{} - {}".format(TemperatureMin, TemperatureMax), chr(176)), "FontSize": 14}
        Fields["3. Precipitation"] = {"Text": "{:3.1f} mm ({:3.1f} mm/h)".format(Precipitation, PrecipitationMax), "FontSize": 10}
        Fields["4. Windspeed"] = {"Text": "{} m/s".format(WindSpeedMax if WindspeedMin is None else "{} - {}".format(WindspeedMin, WindSpeedMax)), "FontSize": 10}

        # Weather symbol
        new_height = self.ImageHeight
        png = wx.Image('pics/{}.png'.format(Symbol), wx.BITMAP_TYPE_ANY)
        png = png.Scale(int(png.GetWidth()/png.GetHeight()*new_height), new_height, wx.IMAGE_QUALITY_HIGH)
        mypic = wx.StaticBitmap(self, -1, wx.Bitmap(png))
        
        for key, textField in sorted(Fields.items()):
            lblField = ST.GenStaticText(self, -1, label=textField["Text"], style=wx.ALIGN_CENTER)
            lblField.SetBackgroundColour("Black")
            lblField.SetForegroundColour("White")
            lblField.SetFont(wx.Font(pointSize=textField["FontSize"], family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            self.sizerMain.Add(lblField, 0, wx.ALIGN_CENTER|wx.ALL, 2)
            if key == "1. Header":
                self.sizerMain.Add(mypic, 0, wx.ALIGN_CENTER| wx.ALL, 2)

        self.SetSizer(self.sizerMain)
        sizerSize = self.sizerMain.GetSize()
        #self.sizerMain.SetMinSize(size=(sizerSize.GetWidth()+5, sizerSize.GetHeight()+5))
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        #blue non-filled rectangle
        dc.SetPen(wx.Pen("Gray", width=1))
        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        sizerSize = self.sizerMain.GetSize()
        dc.DrawRoundedRectangle(0,0, sizerSize.GetWidth(), sizerSize.GetHeight(), 10)
        

class GetSMHIWeather:
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json'
    def __init__(self, userSettings):
        self.places = userSettings['places'] if 'places' in userSettings else {'Skellefteå': {'lat': 64.75203, 'long': 20.95350}}
        
        self.Data = dict()

        for place in self.places:
            self.Data[place] = dict()

    def GetWeather(self):
        cnt = -1
        for place_name, place in self.places.items():
            cnt += 1

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
                self.Data[place_name] = tmp

    def GetMedianWeather(self, PlaceName, LocalTime1, Hours):
        CollectedValues = dict() 

        AddValues = False
        cnt = 0
        for timeValue in self.Data[PlaceName]["timeSeries"]:
            CurrValidTime = datetime.strptime(timeValue["validTime"][:-1] + "+0000", '%Y-%m-%dT%H:%M:%S%z')
            if CurrValidTime - timedelta(hours=1) <= LocalTime1 < CurrValidTime:
                AddValues = True

            if AddValues is False: continue
            cnt += 1
            if cnt > Hours: break

            for parameter in timeValue["parameters"]:
                if parameter["name"] not in CollectedValues:
                    CollectedValues[parameter["name"]] = {"values": [], "unit": parameter["unit"]}

                CollectedValues[parameter["name"]]["values"].append(parameter["values"][0])

        return CollectedValues

                

if __name__ == "__main__":
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


    Weather = GetSMHIWeather(userInput_SMHI)
    Weather.GetWeather()
    Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())
    Tomorrow = (Now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    Weather.GetMedianWeather("Göteborg", Tomorrow, 6)
