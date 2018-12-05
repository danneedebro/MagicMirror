#   -----------------------------
#   |Today                      |
#   -----------------------------
#   |Entry                      |
#   -----------------------------
#   -----------------------------


from datetime import datetime
from datetime import timedelta
import wx
import GoogleCalender.GoogleCalender


class ModuleCalender:
    def __init__(self, mainPanel, update_freq_graphics, update_freq_data):
        self.mainPanel = mainPanel
        self.update_freq_graphics = update_freq_graphics
        self.update_freq_data = update_freq_data
        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()
        self.font_headline = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT, weight=wx.FONTWEIGHT_NORMAL)
        self.font_events = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)

        credentials_filename = 'GoogleCalender/credentials.json'
        token_filenames = ['GoogleCalender/Calender_shared.json', 'GoogleCalender/Calender_personal.json']
        self.data = GoogleCalender.GoogleCalender.GoogleCalender(credentials_filename, token_filenames)

        self.updateDataSet()
        self.update()


    def update(self):
        now = datetime.now()
        self.updated_graphics = now
        self.mainPanel.Freeze()   # Freeze to avoid flickering

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.mainPanel, style=wx.EXPAND|wx.ALIGN_CENTER)
        panel.SetBackgroundColour('Black')
        panel.Freeze()    # Freeze to avoid flickering

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        # Fucked up way to get dateToday with timezone info
        now = datetime.now()
        now = datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S') + '+0100', '%Y-%m-%d %H:%M:%S%z')
        dateToday = now.replace(hour=0, minute=0, second=0, microsecond=0)

        weekDays = {0: 'Måndag', 1: 'Tisdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lördag', 6: 'Söndag'}

        for i in range(0, 8):
            currDay = dateToday + timedelta(days=i)
            dayEmpty = True

            # Print heading with current day
            LblDay = wx.StaticText(panel, label="{} {}".format(weekDays[currDay.weekday()], currDay.strftime('%d %b')))
            LblDay.SetForegroundColour('White')
            LblDay.SetFont(self.font_headline)
            sizerMain.Add(LblDay, 1, wx.ALIGN_LEFT, 2)

            # Loop through all events and determine if that event takes place on current day
            for event in self.data.events:
                start = event['start']['dateTime2']
                end = event['end']['dateTime2']
                if start.strftime('%Y-%m-%d') == currDay.strftime('%Y-%m-%d') or (currDay >= start and currDay < end):
                    dayEmpty = False
                    if 'date' in event['start']:
                        LblEvent = wx.StaticText(panel, label="{}".format(event['summary']))
                        LblEvent.SetForegroundColour('White')
                        LblEvent.SetFont(self.font_events)
                        sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 2)
                    else:
                        LblEvent = wx.StaticText(panel, label="{} {}".format(event['summary'], event['start']['dateTime2'].strftime('%H:%M')))
                        LblEvent.SetForegroundColour('White')
                        LblEvent.SetFont(self.font_events)
                        sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 2)


            if dayEmpty == True:
                LblEvent = wx.StaticText(panel, label="{}".format('(Ingenting)'))
                LblEvent.SetForegroundColour('Gray')
                LblEvent.SetFont(self.font_events)
                sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 2)

        panel.SetSizer(sizerMain)
        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()          # This avoids flickering
        self.mainPanel.Thaw()

    def updateDataSet(self):
        # User input to fetch Google calender data
        self.updated_data = datetime.now()
        print('Hämtar data från Google')
        self.data.update()



