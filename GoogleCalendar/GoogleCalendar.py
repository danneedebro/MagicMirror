from __future__ import print_function

import json

import wx
from datetime import datetime
from datetime import timedelta
import pytz
import wx.lib.stattext as ST

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from operator import itemgetter


class ModuleCalendar:
    NumberOfWeeks = 5
    CalendarData = dict()
    UpdateFrequencyData = 120
    UpdateFrequencyGraphics = 30
    ShowMainCalendar = True
    ShowUpdatedList = True

    def __init__(self, Parent, CalendarSettings, **kwargs):
        self.PanelMain = Parent

        self.UpdateFrequencyData = CalendarSettings["updateFreqData"] if "updateFreqData" in CalendarSettings else self.UpdateFrequencyData
        self.UpdateFrequencyGraphics = CalendarSettings["updateFreqGraphics"] if "updateFreqGraphics" in CalendarSettings else self.UpdateFrequencyGraphics
        self.NumberOfWeeks = CalendarSettings["weeksToPlot"] if "weeksToPlot" in CalendarSettings else self.NumberOfWeeks

        # Read optional keyword arguments
        self.ShowMainCalendar = kwargs["ShowMainCalendar"] if "ShowMainCalendar" in kwargs else self.ShowMainCalendar
        self.ShowUpdatedList = kwargs["ShowUpdatedList"] if "ShowUpdatedList" in kwargs else self.ShowUpdatedList
        self.UpdateFrequencyData = kwargs["UpdateFrequencyData"] if "UpdateFrequencyData" in kwargs else self.UpdateFrequencyData
        self.UpdateFrequencyGraphics = kwargs["UpdateFrequencyGraphics"] if "UpdateFrequencyGraphics" in kwargs else self.UpdateFrequencyGraphics

        self.LastUpdateData = datetime.now() - timedelta(seconds=self.UpdateFrequencyData)
        self.Events = GetGoogleEvents(CalendarSettings)
        self.UpdateData()
        self.LastUpdateGraphics = datetime.now()
        self.Draw()

    def UpdateCheck(self):
        if (datetime.now() - self.LastUpdateData).total_seconds() > self.UpdateFrequencyData:
            self.UpdateData()

        if (datetime.now() - self.LastUpdateGraphics).total_seconds() > self.UpdateFrequencyGraphics:
            self.Draw()

    def UpdateData(self):
        self.LastUpdateData = datetime.now()
        self.Events.GetEvents()

    def Draw(self):
        self.LastUpdateGraphics = datetime.now()
        self.PanelMain.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.PanelMain.GetChildren():
            myobj.DestroyChildren()
            myobj.Destroy()

        panel = wx.Panel(self.PanelMain)
        panel.SetBackgroundColour("Black")

        SizerMain = wx.BoxSizer(wx.VERTICAL)

        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())
        Today = Now.replace(hour=0, minute=0, second=0, microsecond=0)
        ThisMonday = Today - timedelta(days=Today.isoweekday() - 1)

        # Draw main calandar
        if self.ShowMainCalendar:
            SizerFlexGrid = wx.FlexGridSizer(self.NumberOfWeeks+1, 7, 0, 0)

            # Construct an empty 'CalendarData' dict
            self.CalendarData.clear()
            for Day in range(self.NumberOfWeeks*7):
                CurrDate = ThisMonday + timedelta(days=Day)
                self.CalendarData[CurrDate.strftime('%Y-%m-%d')] = {"Events": [], "Date": CurrDate}

            # Populate 'CalendarData' with events
            for event in self.Events.ByDate:
                self.AddEvent(event["Summary"], event["EventStart"], event["EventEnd"])

            # Add a header with weeksdays on blue background    
            for Day in range(7):
                NewBox = MyBox(panel, ThisMonday + timedelta(days=Day), True, BackgroundColour="Blue")
                NewBox.SetBackgroundColour("Blue")
                SizerFlexGrid.Add(NewBox, 0, wx.EXPAND)

            # Loop through 'CalendarData' and create a box for each day
            for Day in sorted(self.CalendarData.keys()):
                CurrDate = self.CalendarData[Day]["Date"]

                NewBox = MyBox(panel, CurrDate, False)
                if CurrDate == Today:
                    NewBox.BorderColour = "Red"
                    NewBox.BorderWidth = 2
                
                for event in self.CalendarData[Day]["Events"]:
                    NewBox.PrintEvent(event["Summary"], event["EventStart"], event["EventEnd"])
                    
                SizerFlexGrid.Add(NewBox, 0, wx.EXPAND)

            SizerMain.Add(SizerFlexGrid)

        # Display a last updated list
        if self.ShowUpdatedList:
            # Add a List with last updated events
            lblNew = ST.GenStaticText(panel, -1, label="Senast uppdaterade")
            lblNew.SetForegroundColour("White")
            lblNew.SetBackgroundColour("Black")
            lblNew.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            SizerMain.Add(lblNew, 0, wx.ALL, 5)

            cnt = 0
            for event in self.Events.ByUpdated:
                if 0 < (Now - event["EventUpdated"]).days > 30:
                    continue
                cnt += 1
                if cnt > 10:
                    break
                SizerEvent = wx.BoxSizer(wx.HORIZONTAL)
                for i in range(2):
                    lblNewString = event["Summary"] if i == 0 else GetEventDate(event["EventStart"], event["EventEnd"])
                    lblNew = ST.GenStaticText(panel, -1, label=lblNewString)
                    lblNew.SetBackgroundColour("Black")
                    lblNew.SetForegroundColour("White" if i == 0 else "Gray")
                    SizerEvent.Add(lblNew, 0, wx.LEFT, 7)

                SizerMain.Add(SizerEvent)

        panel.SetSizerAndFit(SizerMain)
        self.PanelMain.Thaw()

    def AddEvent(self, EventSummary, EventStart, EventEnd):
        for i in range(0, EventEnd.toordinal() - EventStart.toordinal()+1):
            CurrDate = EventStart + timedelta(days=i)
            CurrDateStr = CurrDate.strftime('%Y-%m-%d')
            if CurrDateStr in self.CalendarData:
                if EventStart < self.CalendarData[CurrDateStr]["Date"]:
                    TimeStart = self.CalendarData[CurrDateStr]["Date"]
                else:
                    TimeStart = EventStart

                if EventEnd > self.CalendarData[CurrDateStr]["Date"] + timedelta(days=1):
                    TimeEnd = self.CalendarData[CurrDateStr]["Date"] + timedelta(days=1)
                else:
                    TimeEnd = EventEnd

                self.CalendarData[CurrDateStr]["Events"].append({"Summary": EventSummary, "EventStart": TimeStart, "EventEnd": TimeEnd})




class MyBox(wx.Panel):
    BoxWidth = 130
    BoxHeight = 150
    BorderWidth = 1
    BorderRadius = 0
    BorderColour = "Gray"
    BackgroundColour = "Black"
    CurrDay = 1
    isHeader = False
    def __init__(self, Parent, CurrentDate, isHeader, **kwargs):

        self.BackgroundColour = kwargs["BackgroundColour"] if "BackgroundColour" in kwargs else self.BackgroundColour

        self.CurrentDate = CurrentDate

        if isHeader == True:
            self.BoxHeight = -1
            self.isHeader = True


        wx.Panel.__init__(self, Parent, -1)
        self.SetBackgroundColour("Black")
        self.SizerMain = wx.BoxSizer(wx.VERTICAL)
        self.SizerMain.SetMinSize(size=(self.BoxWidth, self.BoxHeight))

        if isHeader == True:
            WeekDaysInSwedish = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
            lblNew = ST.GenStaticText(self, -1, label=WeekDaysInSwedish[self.CurrentDate.isoweekday()-1], style=wx.ALIGN_CENTER)

            lblNew.SetForegroundColour("White")
            lblNew.SetBackgroundColour(self.BackgroundColour)
            lblNew.SetFont(wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            self.SizerMain.Add(lblNew, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(self.SizerMain)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def PrintEvent(self, EventSummary, EventStart, EventEnd):

        for i in range(2):
            if i == 0:
                lblNewString = "{}-{}".format(EventStart.strftime('%H:%M'),EventEnd.strftime('%H:%M'))
            else:
                if len(EventSummary) > 15:
                    lblNewString = EventSummary[:15] + "\n" + EventSummary[15:]
                else:
                    lblNewString = EventSummary

            lblNew = ST.GenStaticText(self, -1, label=lblNewString)
            lblNew.SetForegroundColour("Gray" if i == 0 else "White")
            lblNew.SetBackgroundColour("Black")
            lblNew.SetFont(wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            if i == 0:
                self.SizerMain.Add(lblNew, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
            else:
                self.SizerMain.Add(lblNew, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        #blue non-filled rectangle
        dc.SetPen(wx.Pen(self.BorderColour, width=self.BorderWidth))
        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        SizerSize = self.SizerMain.GetSize()
        dc.DrawRoundedRectangle(0,0, SizerSize.GetWidth(), SizerSize.GetHeight(), self.BorderRadius)
        
        if self.isHeader is False:
            dc.SetFont(wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground((255,255,0))
            TextSize = dc.GetTextExtent(str(self.CurrentDate.day))
            TextSizeMax = dc.GetTextExtent("30")
            dc.DrawRectangle(SizerSize.GetWidth() - TextSizeMax.GetWidth() - 5, 0, TextSizeMax.GetWidth() + 5, TextSizeMax.GetHeight()+5)
            dc.DrawText(str(self.CurrentDate.day), SizerSize.GetWidth()-TextSize.GetWidth()-3, 3)


class GetGoogleEvents:
    """
    Fetches events from Google Calendars and stores them in two lists, 
        1) self.ByDate      - Events sorted by event start date
        2) self.ByUpdated   - Events sorted by event updated date
    
    """
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

    # Url where credentials file easily can be created
    url_help = 'https://developers.google.com/calendar/quickstart/python'

    def __init__(self, CalendarSettings):

        self.CalendarSettings = CalendarSettings
        self.credentials_filename = CalendarSettings['credentialsFile'] if 'credentialsFile' in CalendarSettings else ''

        self.ByDate = []
        self.ByUpdated = []

        # Check to see if credentials_filename exists
        try:
            fh = open(self.credentials_filename, 'r')

        except FileNotFoundError:
            print('Error: {} doesn\'t exist. Create one at Google APIs console or here: {}'.format(credentials_filename, self.url_help))
            self.status_ok = False
            return

    def _getDateObject(self, str):
        # Input:    str    Datetime in the form YYYY-MM-DDTHH:MM:SS+XX:XX
        # Output    datetime object with correct timezone
        str = str[:len(str)-3] + str[-2:]
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S%z')

    def GetEvents(self):
        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())
        Today = Now.replace(hour=0, minute=0, second=0, microsecond=0)
        ThisMonday = Today - timedelta(days=Today.isoweekday() - 1)
        StartTime1 = ThisMonday.strftime('%Y-%m-%dT%H:%M:%S%z')
        StartTime2 = Now.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S%z')

        self.ByDate.clear()
        self.ByUpdated.clear()

        for calendar_tag, calendar in self.CalendarSettings["calendars"].items():
            token_file = calendar['tokenFile']
            max_results = calendar['maxResults'] if 'maxResults' in calendar else 100
            calendar_id = calendar['id'] if 'id' in calendar else 'primary'
            track_updates = calendar['trackUpdates'] if 'trackUpdates' in calendar else True

            store = file.Storage(token_file)
            creds = store.get()

            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(self.credentials_filename, self.SCOPES)
                creds = tools.run_flow(flow, store)
            service = build('calendar', 'v3', http=creds.authorize(Http()))

            # Call the Calendar API
            for i in range(2):
                print("Läser in kalender {}, index={}".format(calendar_id, i))
                if i == 0:
                    NewEvents = service.events().list(calendarId=calendar_id, timeMin=StartTime1, maxResults=max_results,
                                                      singleEvents=True, orderBy='startTime').execute()
                elif i == 1:
                    if track_updates is False:
                        break
                    NewEvents = service.events().list(calendarId=calendar_id, timeMin=StartTime2, maxResults=max_results,
                                                      singleEvents=False, orderBy='updated').execute()

                events = NewEvents.get('items', [])

                if not events:
                    print('Info ' + now.strftime('(%Y-%m-%d %H:%M): ') + 'No upcoming events found')

                # Loop through events and add a dateTime object in current event called 'dateTimeStart' and 'dateTimeEnd'
                for event in events:
                    EventSummary = event["summary"] if "summary" in event else "(Ingen titel)"
                    EventUpdated = datetime.strptime(event['updated'][:-1]+"+0000", '%Y-%m-%dT%H:%M:%S.%f%z')

                    if 'date' in event['start']:    # if whole-day activity
                        EventStart = pytz.timezone('Europe/Stockholm').localize(datetime.strptime(event['start']['date'], '%Y-%m-%d'))
                        EventEnd = pytz.timezone('Europe/Stockholm').localize(datetime.strptime(event['end']['date'], '%Y-%m-%d')) - timedelta(minutes=1)
                    elif 'dateTime' in event['start']:   # If
                        EventStart = self._getDateObject(event['start']['dateTime'])
                        EventEnd = self._getDateObject(event['end']['dateTime'])

                    if i == 0:
                        self.ByDate.append({"Summary": EventSummary, "EventStart": EventStart, "EventEnd": EventEnd, "EventUpdated": EventUpdated, "CalendarId": calendar_id})
                    else:
                        self.ByUpdated.append({"Summary": EventSummary, "EventStart": EventStart, "EventEnd": EventEnd, "EventUpdated": EventUpdated, "CalendarId": calendar_id})

        # Sort list
        self.status_ok = True

        self.ByDate = sorted(self.ByDate, key=itemgetter('EventStart'))
        self.ByUpdated = sorted(self.ByUpdated, key=itemgetter('EventUpdated'), reverse=True)




# Static functions
def GetEventDate(EventStart, EventEnd):
    WeekDaysShort = ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]
    MonthsShort = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
    if EventStart.day == EventEnd.day:
        return "{} {} {} {}-{}".format(WeekDaysShort[EventStart.isoweekday()-1], EventStart.day, MonthsShort[EventStart.month-1], EventStart.strftime("%H:%M"), EventEnd.strftime("%H:%M"))
    else:
        return "{} {} {} {}-{}".format(WeekDaysShort[EventStart.isoweekday()-1], EventStart.day, MonthsShort[EventStart.month-1], EventStart.strftime("%H:%M"), EventEnd.strftime("%H:%M"))
