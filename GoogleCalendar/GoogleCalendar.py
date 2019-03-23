from __future__ import print_function

import wx
from datetime import datetime
from datetime import timedelta
import pytz
import wx.lib.stattext as ST

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from operator import itemgetter

class ModuleGoogleCalendar:
    def __init__(self, panel_main, userSettings):
        self.panel_main = panel_main

        self.updateFreqData = userSettings['updateFreqData'] if 'updateFreqData' in userSettings else 600
        self.updateFreqGraphics = userSettings['updateFreqGraphics'] if 'updateFreqGraphics' in userSettings else 60

        self.days_to_plot_in_detail = userSettings['daysToZoom'] if 'daysToZoom' in userSettings else 7
        self.days_to_plot_total = userSettings['daysToPlot'] if 'daysToPlot' in userSettings else 14

        self.calendars = userSettings['calendars'] if 'calendars' in userSettings else {'None': {'id': '', 'tokenFile': '', 'maxResults': 100, 'textColor': '', 'trackUpdates': True}}
        self.credentials_filename = userSettings['credentialsFile'] if 'credentialsFile' in userSettings else ''

        self.repaint_completely = False   # Flag to fix problem with text residues. Causes som flicker so it's best to
                                          # only set this to flag True when dataset is refreshed

        self.Update()

    def UpdateCheck(self):
        if (datetime.now() - self.updated_data).total_seconds() > self.updateFreqData:
            self.Update()

    def Update(self):
        """Fetches events from Google and redraws events to Calendar"""
        self.updated_data = datetime.now()

        #self.EventsByDate = 
        self.data = GetGoogleEvents(self.credentials_filename, self.calendars)

        self.Calendar = CalendarBoxes(self.panel_main)
        for event in self.data.EventsSortedByDate:
            self.Calendar.AddEvent(event['summary'], event['EventStart'], event['EventEnd'])

        cnt = 0
        for event in self.data.EventsSortedByUpdated:
            cnt += 1
            if cnt > 10:
                break
            self.Calendar.AddEventLastUpdated(event['summary'], event['EventStart'], event['EventEnd'])


        self.Calendar.Draw()




class CalendarBoxes:
    BoxWidth: int = 130
    BoxHeight: int = 130
    Weeks: int = 4
    DataSet: dict = dict()
    Events: dict = dict()
    EventsLastUpdated: list = list()

    def __init__(self, MainPanel: wx.Panel):
        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())

        Today = Now.replace(hour=0, minute=0, second=0, microsecond=0)
        ThisMonday = Today - timedelta(days=datetime.today().isoweekday() % 7 - 1)
        
        self.MainPanel = MainPanel
        
        for WeekInd in range(self.Weeks):
            for WeekDay in range(7):
                CurrDate = ThisMonday + timedelta(days=WeekInd*7 + WeekDay)
                self.DataSet[CurrDate.strftime('%Y-%m-%d')] = {"events": [], "date": CurrDate}

        self.EventsLastUpdated = []

        self.FontHeader = wx.Font(pointSize=16, family=wx.DECORATIVE, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.FontHeader2 = wx.Font(pointSize=13, family=wx.DECORATIVE, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.font2 = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)


    def AddEvent(self, EventSummary: str, EventStart: datetime, EventEnd: datetime):
        """
        Adds an event to DataSet

        Input:
            EventSummary (string) = Title/ Summary of event
            EventStart (datetime) = Start time of event
            EventEnd (datetime) = End time of event
        """
        for i in range((EventEnd - EventStart).days+1):
            CurrDate = EventStart + timedelta(days=i)
            CurrDay = CurrDate.strftime('%Y-%m-%d')
            if CurrDay in self.DataSet:
                if EventStart < self.DataSet[CurrDay]["date"]:
                    TimeStart = self.DataSet[CurrDay]["date"]
                else:
                    TimeStart = EventStart

                if EventEnd > self.DataSet[CurrDay]["date"] + timedelta(days=1):
                    TimeEnd = self.DataSet[CurrDay]["date"] + timedelta(days=1)
                else:
                    TimeEnd = EventEnd

                self.DataSet[CurrDate.strftime('%Y-%m-%d')]["events"].append({"summary": EventSummary, "start": TimeStart, "end": TimeEnd})

    def AddEventLastUpdated(self, EventSummary: str, EventStart: datetime, EventEnd: datetime):
        self.EventsLastUpdated.append({"summary": EventSummary, "start": EventStart, "end": EventEnd})    

    def Draw(self):
        """
        Draws a Calandar inside self.MainPanel
        """
        Now = pytz.timezone('Europe/Stockholm').localize(datetime.now())
        Today = Now.replace(hour=0, minute=0, second=0, microsecond=0)

        self.MainPanel.Freeze()

        # Delete all objects in main container for this module
        for myobj in self.MainPanel.GetChildren():
            myobj.DestroyChildren()
            myobj.Destroy()

        panel = wx.Panel(self.MainPanel)

        sizerMain = wx.BoxSizer(wx.VERTICAL)
        
        sizerFlexGrid = wx.FlexGridSizer(self.Weeks, 7, 0, 0)

        for day in self.DataSet:
            IsToday = True if day == datetime.now().strftime('%Y-%m-%d') else False
            if self.DataSet[day]["date"] >= Today:
                TextColor = "White"
            else:
                TextColor = "Gray"

            SubPanel = wx.Panel(panel, -1, style=wx.BORDER_RAISED if IsToday == True else wx.BORDER_STATIC)
            
            SubPanel.SetForegroundColour("White")
            sizerCalendarBox = wx.BoxSizer(wx.VERTICAL)
            sizerCalendarBox.SetMinSize(size=(self.BoxWidth, self.BoxHeight))

            sizerHeader = wx.BoxSizer(wx.HORIZONTAL)
            sizerHeader.SetMinSize(size=(self.BoxWidth, -1))
            Days = ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]
            Months = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]

            # i = 0  is label containing the day, i = 1 is label containing date
            for i in range(2):
                lblNewString = Days[self.DataSet[day]["date"].weekday()] if i == 0 else str(self.DataSet[day]["date"].day) + " " + Months[self.DataSet[day]["date"].month-1]
                lblNew = ST.GenStaticText(SubPanel, label=lblNewString, style=wx.ALIGN_LEFT if i == 0 else wx.ALIGN_RIGHT)
                lblNew.SetForegroundColour(TextColor)
                lblNew.SetBackgroundColour("Black")
                lblNew.SetFont(self.FontHeader if i == 0 else self.FontHeader2)
                sizerHeader.Add(lblNew, 1, wx.ALIGN_BOTTOM)

            sizerCalendarBox.Add(sizerHeader, 0, wx.LEFT | wx.RIGHT, 5)   # Proportion 0 to stack tight

            # Loop through days events and and them to sizerRight
            for event in self.DataSet[day]["events"]:
                sizerEvent = wx.BoxSizer(wx.VERTICAL)
                for i in range(2):
                    lblNewString = event["summary"] if i == 1 else "{}-{}".format(event["start"].strftime('%H:%M'), event["end"].strftime('%H:%M'))
                    lblNew = ST.GenStaticText(SubPanel, label=lblNewString)
                    lblNew.SetForegroundColour(TextColor if i == 1 else "Gray")
                    lblNew.SetBackgroundColour("Black")
                    sizerCalendarBox.Add(lblNew, 0, wx.LEFT, 5)    # Proportion 0 to stack tight

            sizerFlexGrid.Add(SubPanel, 1, wx.EXPAND)
            SubPanel.SetSizer(sizerCalendarBox)
            SubPanel.Fit()
            #sizerCalendarBox.Fit(SubPanel)   # Fit to sizer's min size
            
        sizerLastUpdatedList = wx.BoxSizer(wx.VERTICAL)

        lblLastUpdated = ST.GenStaticText(self.MainPanel, label="Senast uppdaterad")
        lblLastUpdated.SetForegroundColour("White")
        lblLastUpdated.SetBackgroundColour("Black")
        lblLastUpdated.SetFont(self.font2)
        sizerLastUpdatedList.Add(lblLastUpdated)

        sizerMain.Add(sizerFlexGrid)
        sizerMain.Add(sizerLastUpdatedList)

        for event in self.EventsLastUpdated:
            sizerEvent = wx.BoxSizer(wx.HORIZONTAL)
            for i in range(2):
                lblNewString = event['summary'] if i == 0 else "{} {} {}, {}".format(Days[event["start"].weekday()], event['start'].day, Months[event["start"].month-1], event["start"].strftime('%H:%M'))
                lblNew = ST.GenStaticText(panel, label=lblNewString)
                lblNew.SetForegroundColour("White" if i == 0 else "Gray")
                lblNew.SetBackgroundColour("Black")
                sizerEvent.Add(lblNew, 0, wx.LEFT, 3)
            
            sizerMain.Add(sizerEvent)

        panel.SetSizer(sizerMain)
        panel.Fit()
        #sizerMain.SetSizeHints(self.MainPanel)
        
        self.MainPanel.Thaw()
        #self.MainPanel.Fit()
        



        
      


class GetGoogleEvents:
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

    # Url where credentials file easily can be created
    url_help = 'https://developers.google.com/calendar/quickstart/python'

    def __init__(self, credentials_filename, calendars_input, *args, **kwargs):

        self.calendars_input = calendars_input

        # Check to see if credentials_filename exists
        try:
            fh = open(credentials_filename, 'r')
            # Store configuration file values

            self.credentials_filename = credentials_filename
            self.Events = []
            self.GetEvents()

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
        ThisMonday = Now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=datetime.today().isoweekday() % 7 - 1)
        StartTime1 = ThisMonday.strftime('%Y-%m-%dT%H:%M:%S%z')
        StartTime2 = Now.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S%z')

        self.EventsSortedByDate = []
        self.EventsSortedByUpdated = []

        for calendar_tag, calendar in self.calendars_input.items():
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
                    if 'date' in event['start']:    # if whole-day activity
                        event['EventStart'] = pytz.timezone('Europe/Stockholm').localize(datetime.strptime(event['start']['date'], '%Y-%m-%d'))
                        event['EventEnd'] = pytz.timezone('Europe/Stockholm').localize(datetime.strptime(event['end']['date'], '%Y-%m-%d')) - timedelta(minutes=1)
                        event['start']['dateTime2'] = datetime.strptime(event['start']['date'] + ' +0100', '%Y-%m-%d %z')
                        #event['end']['dateTime2'] = datetime.strptime(event['end']['date']+ ' +0100', '%Y-%m-%d %z')
                        event['dateTimeStart'] = event['start']['dateTime2'].strftime('%Y-%m-%d %H:%M:%S')
                    elif 'dateTime' in event['start']:   # If
                        event['EventStart'] = self._getDateObject(event['start']['dateTime'])
                        event['EventEnd'] = self._getDateObject(event['end']['dateTime'])
                        event['start']['dateTime2'] = self._getDateObject(event['start']['dateTime'])
                        event['end']['dateTime2'] = self._getDateObject(event['end']['dateTime'])
                        event['dateTimeStart'] = event['start']['dateTime2'].strftime('%Y-%m-%d %H:%M:%S')

                for event in events:
                    if 'summary' not in event:
                        event['summary'] = '(Ingen titel)'
                    if i == 0:
                        self.EventsSortedByDate.append(event)
                    else:
                        self.EventsSortedByUpdated.append(event)




        # Sort list
        self.status_ok = True

        self.EventsSortedByDate = sorted(self.EventsSortedByDate, key=itemgetter('dateTimeStart'), reverse=False)
        self.EventsSortedByUpdated = sorted(self.EventsSortedByUpdated, key=itemgetter('updated'), reverse=True)
