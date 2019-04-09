import wx
import wx.lib.stattext as ST
import requests
import base64
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
#import VastTrafik.VastTrafik
import logging

logger = logging.getLogger("MagicMirror")

class ModuleVastTrafik:
    def __init__(self, mainPanel, userSettings):
        self.mainPanel = mainPanel

        self.updateFreqData = userSettings['updateFreqData'] if 'updateFreqData' in userSettings else 60
        self.updateFreqGraphics = userSettings['updateFreqGraphics'] if 'updateFreqGraphics' in userSettings else 10

        font_size = 10

        key = userSettings['tokenKey'] if 'tokenKey' in userSettings else ''
        secret = userSettings['tokenSecret'] if 'tokenSecret' in userSettings else ''
        stopId = userSettings['stopId'] if 'stopId' in userSettings else ''
        
        self.LastUpdateGraphics = datetime.now()
        self.LastUpdateData = datetime.now()
        
        self.data = VastTrafik(key, secret, stopId)
        self.UpdateGraphics()

    def UpdateCheck(self):
        now = datetime.now()

        if (now - self.LastUpdateGraphics).seconds >= self.updateFreqGraphics:
            try:
                self.UpdateGraphics()
            except Exception as e:
                logger.error("Unexpected error updating graphics: {}".format(e), exc_info=True)

        if (now - self.LastUpdateData).seconds >= self.updateFreqData:
            try:
                self.UpdateDataSet()
            except Exception as e:
                logger.error("Unexpected error updating dataset: {}".format(e), exc_info=True)
            


    def UpdateDataSet(self):
        self.LastUpdateData = datetime.now()
        self.data.update()

    def UpdateGraphics(self):
        self.LastUpdateGraphics = datetime.now()
        self.mainPanel.Freeze()   # Freeze to avoid flickering

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.mainPanel, style=wx.EXPAND|wx.ALIGN_CENTER)
        panel.SetBackgroundColour('Black')
        panel.Freeze()    # Freeze to avoid flickering

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        departureTable1 = DepartureTable(panel, "Svingeln mot stan {}".format(self.data.departures['localDateTime'].strftime('%H:%M')))
        for departure in self.data.departures["Departures"]:
            if departure["track"][0] not in ("A", "C", "E"):
                continue
            departureTable1.AddRow(departure, self.data.departures['serverDateTime'], self.data.departures['localDateTime'])

        departureTable2 = DepartureTable(panel, "Svingeln från stan {}".format(self.data.departures['localDateTime'].strftime('%H:%M')))
        for departure in self.data.departures["Departures"]:
            if departure["track"][0] not in ("B", "D", "F", "G"):
                continue
            departureTable2.AddRow(departure, self.data.departures['serverDateTime'], self.data.departures['localDateTime'])

        # Add header staticText and flex grid sizer to main (vertical) boxsizer
        sizerMain.Add(departureTable1, 0, wx.ALL|wx.EXPAND, 5)
        sizerMain.Add(departureTable2, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizerMain)
        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()          # This avoids flickering
        self.mainPanel.Thaw()


class DepartureTable(wx.Panel):
    FontSize = 10

    def __init__(self, Parent, HeaderText):
        wx.Panel.__init__(self, Parent, -1)
        self.SetBackgroundColour("Black")
        
        sizerMain = wx.BoxSizer(wx.VERTICAL)
        self.sizerTable = wx.FlexGridSizer(7, 2, 2)
        self.sizerTable.AddGrowableCol(1, 1)
        lblTitle = ST.GenStaticText(self, -1, label=HeaderText)
        lblTitle.SetForegroundColour("white")
        lblTitle.SetBackgroundColour("black")
        lblTitle.SetFont(wx.Font(pointSize=self.FontSize, family=wx.FONTFAMILY_MODERN, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
        
        sizerMain.Add(lblTitle)
        sizerMain.Add(self.sizerTable, 0, wx.EXPAND)

        self.SetSizer(sizerMain)

    def AddRow(self, departure, serverDateTime, localDateTime):
        now = datetime.now()

        deltaTime1 = departure['dateTime'][0] - serverDateTime - (now - localDateTime)
        timeToDeparture1 = str(int(round(deltaTime1.seconds/60,0))) if deltaTime1.days >= 0 else 'Nu'
        accessibility1 = "\u267f" if departure["accessibility"][0] == "wheelChair" else ""
        
        if len(departure['dateTime']) > 2:
            deltaTime2 = departure['dateTime'][1] - serverDateTime - (now - localDateTime)
            timeToDeparture2 = str(int(round(deltaTime2.seconds / 60, 0))) if deltaTime2.days >= 0 else 'Nu'
            accessibility2 = '\u267f' if departure['accessibility'][1] == 'wheelChair' else ''
        else:
            timeToDeparture2 = ''
            accessibility2 = ''

        cellProperties = dict()
        cellProperties[0] = {"Text": departure["sname"][0].center(7, ' '), "backgroundColor": departure['fgColor'][0], "textColor": departure['bgColor'][0]} # Note bgColor means textcolor in Vasttrafik API
        cellProperties[1] = {"Text": "{:15.12}".format(departure['direction'][0]), "backgroundColor": "black", "textColor": "white"}
        cellProperties[2] = {"Text": "{:>5}".format(timeToDeparture1), "backgroundColor": "black", "textColor": "white"}
        cellProperties[3] = {"Text": accessibility1, "backgroundColor": "black" if accessibility1 == "" else "blue", "textColor": "white"}
        cellProperties[4] = {"Text": "{:>5}".format(timeToDeparture2), "backgroundColor": "black", "textColor": "white"}
        cellProperties[5] = {"Text": accessibility2, "backgroundColor": "black" if accessibility2 == "" else "blue", "textColor": "white"}
        cellProperties[6] = {"Text": "{:>2}".format(departure['track'][0]), "backgroundColor": "black", "textColor": "white"}

        for key, cellProperty in sorted(cellProperties.items(), reverse=False):
            lblNew = ST.GenStaticText(self, -1, label=cellProperty["Text"])
            lblNew.SetForegroundColour(cellProperty["textColor"])
            lblNew.SetBackgroundColour(cellProperty["backgroundColor"])
            lblNew.SetFont(wx.Font(pointSize=self.FontSize, family=wx.FONTFAMILY_MODERN, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            self.sizerTable.Add(lblNew, 0)




class VastTrafik:
    url_token = 'https://api.vasttrafik.se/token'
    url_departureBoard = 'https://api.vasttrafik.se/bin/rest.exe/v2/departureBoard'

    def __init__(self, key, secret, location_id):
        self.key = key
        self.secret = secret
        self.location_id = location_id
        self.access_token_expires = datetime.now() - timedelta(seconds=2)
        self.get_departures()

    def get_access_token(self):
        now = datetime.now()
        parameters = {'format': 'json', 'grant_type': 'client_credentials'}
        url = self.url_token
        head = {'Authorization': 'Basic ' + base64.b64encode((self.key + ':' + self.secret).encode()).decode(),
                'Content-Type': 'application/x-www-form-urlencoded'}

        r = requests.post(url, headers=head, params=parameters)

        if r.status_code == 200:
            tmp = r.json()
            self.status_ok = True
        else:
            print('Error while updating VästTrafik access token' + now.strftime('(%Y-%m-%d %H:%M): ') + str(r.status_code) + str(r.content))
            self.status_ok = False
            return

        self.access_token = tmp['access_token']
        self.access_token_expires = datetime.now() + timedelta(seconds=tmp['expires_in'])

    def update(self):
        self.get_departures()

    def get_departures(self):
        now = datetime.now()

        # If access token has expired, request new using method get_access_token
        if self.access_token_expires < now:
            print('Info ' + now.strftime('(%Y-%m-%d %H:%M): ') + 'Access token expired, requesting new')
            self.get_access_token()


        # Step 3: Get list of depatures using api method 'departureBoard'
        url = self.url_departureBoard
        parameters = {'format': 'json', 'id': self.location_id, 'date': now.strftime("%Y-%m-%d"), 'time': now.strftime("%H:%M"), 'timeSpan': 60}
        head = {'Authorization': 'Bearer ' + self.access_token}

        r = requests.get(url, headers=head, params=parameters)

        if r.status_code == 200:
            tmp = r.json()
            self.status_ok = True
        else:
            print('Error during VästTrafik departureBoard call' + now.strftime('(%Y-%m-%d %H:%M): ') + str(r.status_code) + str(r.content))
            self.status_ok = False
            return
            #tmp = {'DepartureBoard':{'servertime': now.strftime('%H:%M'), 'serverdate': now.strftime('%Y-%m-%d'), 'Departure'}}

        if "DepartureBoard" not in tmp:
            logger.error("Key error, \"DepartureBoard\" not in response")
            return

        serverDate = tmp["DepartureBoard"].get("serverdate", now.strftime("%Y-%m-%d"))
        serverTime = tmp["DepartureBoard"].get("servertime", now.strftime("%H:%M"))
        serverDateTime = datetime.strptime("{} {}".format(serverDate, serverTime), "%Y-%m-%d %H:%M")
        departure_board = {'serverDateTime': serverDateTime, 'localDateTime': now, 'Departures': []}

        missingkeydict = {'accessibility': '', 'track': '', 'rtTrack': '', 'rtTime': '', 'rtDate': '', 'time': '', 'date': ''}
        # Loop through and change values for each departure to a list (in order to use append command)
        for i in range(0, len(tmp['DepartureBoard']['Departure'])):
            currItem = tmp['DepartureBoard']['Departure'][i]
            new_dict = {}
            for key in currItem:
                new_dict[key] = [currItem[key]]
            if 'rtTime' in currItem:
                new_dict['dateTime'] = [datetime.strptime(currItem['rtDate'] + ' ' + currItem['rtTime'], "%Y-%m-%d %H:%M")]
                new_dict['isRealTime'] = [True]
            elif 'time' in currItem:
                new_dict['dateTime'] = [datetime.strptime(currItem['date'] + ' ' + currItem['time'], "%Y-%m-%d %H:%M")]
                new_dict['isRealTime'] = [False]

            # Check of optional keys is missing and add them
            for key in missingkeydict:
                if key not in currItem:
                    new_dict[key] = [missingkeydict[key]]

            departure_board['Departures'].append(new_dict)  # Append new_dict to list

        # Sort list
        departure_board['Departures'] = sorted(departure_board['Departures'], key=itemgetter('dateTime'), reverse=False)


        # Loop through departures and collect them after 'sname' and 'track'.If found append values and delete dict item
        i = 0
        while i < len(departure_board['Departures']):
            target = departure_board['Departures'][i]   # The departure item to look for
            j = i + 1
            while j < len(departure_board['Departures']):
                candidate = departure_board['Departures'][j]  # Current departure item

                if target['sname'][0] == candidate['sname'][0] and target['track'][0] == candidate['track'][0]:
                    for key in candidate:
                        if key in target:
                            target[key].append(candidate[key][0])
                        else:   # If key doesn't exist in target, add empty strings as many
                            target[key] = []
                            for k in range(0, len(target['name'])):
                                target[key].append('')

                    del departure_board['Departures'][j]   # Delete candidate departure item
                else:
                    j = j + 1
            i = i + 1


        self.departures = departure_board
        #self.departures['DepartureBoard']['lastrequest'] = now   # time for last request

