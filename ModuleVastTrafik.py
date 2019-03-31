from datetime import datetime
import wx
import wx.lib.stattext as ST
import VastTrafik.VastTrafik


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
        
        self.data = VastTrafik.VastTrafik.VastTrafik(key, secret, stopId)
        self.UpdateGraphics()

    def UpdateCheck(self):
        now = datetime.now()

        if (now - self.LastUpdateGraphics).seconds >= self.updateFreqGraphics:
            self.UpdateGraphics()

        if (now - self.LastUpdateData).seconds >= self.updateFreqData:
            self.UpdateDataSet()

    def UpdateDataSet(self):
        self.LastUpdateData = datetime.now()
        print('Hämtar data från VästTrafik')
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




