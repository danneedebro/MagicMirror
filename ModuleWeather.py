from datetime import datetime
from datetime import timedelta
import requests
import wx
import wx.lib.stattext as ST
import pytz

import json   # REMOVE

class ModuleWeather:
    url = 'https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{}/lat/{}/data.json'
    timezone = pytz.timezone('Europe/Stockholm')
    weather_symb = {1: "Klart", 2: "Lätt molnighet", 3: "Halvklart", 4: "Molnigt", 5: "Mycket moln", 6: "Mulet",
                    7: "Dimma", 8: "Lätt regnskur", 9: "Regnskur", 10: "Kraftig regnskur", 11: "Åskskur",
                    12: "Lätt by av regn och snö", 13: "By av regn och snö", 14: "Kraftig by av regn och snö",
                    15: "Lätt snöby", 16: "Snöby", 17: "Kraftig snöby", 18: "Lätt regn", 19: "Regn",
                    20: "Kraftigt regn", 21: "Åska", 22: "Lätt snöblandat regn", 23: "Snöblandat regn",
                    24: "Kraftigt snöblandat regn", 25: "Lätt snöfall", 26: "Snöfall", 27: "Ymnigt snöfall"}

    def __init__(self, Parent, userSettings):
        self.PanelMain = Parent

        self.updateFreqData = userSettings['updateFreqData'] if 'updateFreqData' in userSettings else 600
        self.updateFreqGraphics = userSettings['updateFreqGraphics'] if 'updateFreqGraphics' in userSettings else 60
        
        self.places = userSettings['places'] if 'places' in userSettings else {'Skellefteå': {'lat': 64.75203, 'long': 20.95350}}
        
        self.Weather = GetSMHIWeather(userSettings)
        self.UpdateData()
        
        self.UpdateGraphics()
        

    def UpdateCheck(self):
        now = datetime.now()
        if (now - self.LastUpdateData).total_seconds() > 600:
            self.UpdateData()

        if (now - self.LastUpdateGraphics).total_seconds() > 60:
            self.UpdateGraphics()

    def UpdateData(self):
        self.LastUpdateData = datetime.now()
        self.Weather.GetWeather()


    def UpdateGraphics(self):
        self.LastUpdateGraphics = datetime.now()

        self.PanelMain.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.PanelMain.GetChildren():
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.PanelMain)
        panel.SetBackgroundColour('Black')

        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())

        sizerMain = wx.BoxSizer(wx.VERTICAL)
        weatherTable = WeatherTable(panel)

        weatherCurr = self.Weather.GetMedianWeather("Göteborg", Now, 1)
        symb = weatherCurr["Wsymb2"]["values"][0]
        Tmin, Tmax = (weatherCurr["t"]["values"][0], weatherCurr["t"]["values"][0])
        pmean, pmax = (weatherCurr["pmean"]["values"][0], weatherCurr["pmax"]["values"][0])
        wsMin, wsMax = (weatherCurr["ws"]["values"][0], weatherCurr["ws"]["values"][0])
        weatherTable.AddRow("Nu", symb, Tmin, Tmax, pmean, pmax, wsMin, wsMax, 0, 0, 3, 7)

        weatherNext8h = self.Weather.GetMedianWeather("Göteborg", Now, 8)
        symb = int(sum(weatherNext8h["Wsymb2"]["values"])/len(weatherNext8h["Wsymb2"]["values"]))
        Tmin, Tmax = (min(weatherNext8h["t"]["values"]), max(weatherNext8h["t"]["values"]))
        pmean, pmax = (sum(weatherNext8h["pmean"]["values"]), max(weatherNext8h["pmax"]["values"]))
        wsMin, wsMax = (min(weatherNext8h["ws"]["values"]), max(weatherNext8h["ws"]["values"]))
        weatherTable.AddRow("Nästa 8h", symb, Tmin, Tmax, pmean, pmax, wsMin, wsMax, 0, 0, 3, 7)

        sizerMain.Add(weatherTable)
        #weatherNext8h = self.Weather.GetMedianWeather("Göteborg", Now, 8)
        #tempNext8h = str(min(weatherNext8h["t"]["values"])) + "-" + str(max(weatherNext8h["t"]["values"])) 
        #WeatherBox1 = WeatherBox(panel, "Nästa 8h", tempNext8h, weatherNext8h["Wsymb2"]["values"][0], 75)
        #SizerMain.Add(WeatherBox1)

        panel.SetSizerAndFit(sizerMain)
        self.PanelMain.Thaw()



class WeatherTable(wx.Panel):
    ImageHeight = 80
    FontSizeTemp = 54
    FontSizeOther = 14
    def __init__(self, Parent):
        wx.Panel.__init__(self, Parent, -1)
        self.SetBackgroundColour("Black")
        self.sizerMain = wx.FlexGridSizer(5, 5, 5)
        self.SetSizer(self.sizerMain)



    def AddRow(self, Header, Symbol, TemperatureMin, TemperatureMax, Precipitation, PrecipitationMax, WindspeedMin, \
               WindSpeedMax, WindDirection1, WindDirection2, WindGustMin, WindGustMax):
        """Adds a row to weather table"""
        # Header / Title
        lblTitle = ST.GenStaticText(self, -1, label=Header, style=wx.ALIGN_CENTER)
        lblTitle.SetBackgroundColour("Black")
        lblTitle.SetForegroundColour("White")
        lblTitle.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
        self.sizerMain.Add(lblTitle, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # Weather symbol
        new_height = self.ImageHeight
        png = wx.Image('pics/{}.png'.format(Symbol), wx.BITMAP_TYPE_ANY)
        png = png.Scale(int(png.GetWidth()/png.GetHeight()*new_height), new_height, wx.IMAGE_QUALITY_HIGH)
        mypic = wx.StaticBitmap(self, -1, wx.Bitmap(png))
        self.sizerMain.Add(mypic, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        # Temperature
        sizerVert = wx.BoxSizer(wx.VERTICAL)
        for i in range(1):
            lblNew = ST.GenStaticText(self, -1, label="{}-{}{}C".format(TemperatureMin, TemperatureMax, chr(176)), style=wx.ALIGN_RIGHT)
            lblNew.SetBackgroundColour("Black")
            lblNew.SetForegroundColour("White")
            lblNew.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            sizerVert.Add(lblNew, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.sizerMain.Add(sizerVert, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        # Precipitation
        sizerVert = wx.BoxSizer(wx.VERTICAL)
        for i in range(2):
            lblNew = ST.GenStaticText(self, -1, label="{} {}".format(Precipitation if i==0 else PrecipitationMax, "mm" if i==0 else "mm/h"), style=wx.ALIGN_RIGHT)
            lblNew.SetBackgroundColour("Black")
            lblNew.SetForegroundColour("White")
            lblNew.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            sizerVert.Add(lblNew, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.sizerMain.Add(sizerVert, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        # Wind speed + wind gust
        sizerVert = wx.BoxSizer(wx.VERTICAL)
        for i in range(2):
            lblNew = ST.GenStaticText(self, -1, label="{}-{} m/s".format(WindspeedMin if i==0 else WindGustMin, WindSpeedMax if i==0 else WindGustMax), style=wx.ALIGN_CENTER)
            lblNew.SetBackgroundColour("Black")
            lblNew.SetForegroundColour("White")
            lblNew.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            sizerVert.Add(lblNew, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.sizerMain.Add(sizerVert, 0, wx.ALIGN_CENTER_VERTICAL, 5)




        








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
                self.Data[place_name] = tmp

    def GetMedianWeather(self, PlaceName, LocalTime1, Hours):
        CollectedValues = dict() 

        AddValues = False
        cnt = 0
        for timeValue in self.Data[PlaceName]["timeSeries"]:
            CurrValidTime = datetime.strptime(timeValue["validTime"][:-1] + "+0000", '%Y-%m-%dT%H:%M:%S%z')
            if CurrValidTime - timedelta(hours=1) <= LocalTime1 < CurrValidTime:
                AddValues = True

            if AddValues is False:
                continue
            cnt += 1
            if cnt > Hours:
                break

            print(CurrValidTime.strftime('%Y-%m-%d %H:%M:%S.%f%z'))

            for parameter in timeValue["parameters"]:
                if parameter["name"] not in CollectedValues:
                    CollectedValues[parameter["name"]] = {"values": [], "unit": parameter["unit"]}

                CollectedValues[parameter["name"]]["values"].append(parameter["values"][0])

        return CollectedValues

                


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
