"""
Graphic module for Google Calender data

"""

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
import pytz

class ModuleCalender:
    def __init__(self, mainPanel, *args, **kwargs): #update_freq_graphics, update_freq_data):
        """
        Constructor. Creates a graphical module to display Google Calender data

        Args:
            mainPanel:                  wx.Panel object for the container/panel that holds the other widgets
            update_freq_graphics (int): Time in seconds between updates of the graphical module
            update_freq_data (int):     Time in seconds between fetching data from Google

        """

        self.mainPanel = mainPanel

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 30
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 60
        self.days_to_plot_in_detail = kwargs['days_to_plot_in_detail'] if 'days_to_plot_in_detail' in kwargs else 7
        self.days_to_plot_total = kwargs['days_to_plot_total'] if 'days_to_plot_total' in kwargs else 14

        self.repaint_completely = False   # Flag to fix problem with text residues. Causes som flicker so it's best to
                                          # only set this to flag True when dataset is refreshed

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()
        self.font_headline = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.font_events = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        self.font_events_slant = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT, weight=wx.FONTWEIGHT_NORMAL)
        self.font_last_updated = wx.Font(pointSize=9, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        credentials_filename = 'GoogleCalender/credentials.json'
        token_filenames = ['GoogleCalender/Calender_shared.json', 'GoogleCalender/Calender_personal.json']
        self.data = GoogleCalender.GoogleCalender.GoogleCalender(credentials_filename, token_filenames)

        self.updateDataSet()
        self.update()


    def update(self):
        """
        Updates the graphics

        Step 1. Delete all objects in mainPanel
        Step 2. Creates StaticText objects that are added to a boxsizer (Vertical)

        """
        now = datetime.now()
        self.updated_graphics = now
        if self.repaint_completely == False:
            self.mainPanel.Freeze()   # Freeze to avoid flickering

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            myobj.DestroyChildren()
            myobj.Destroy()


        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.mainPanel, style=wx.EXPAND|wx.ALIGN_CENTER | wx.FULL_REPAINT_ON_RESIZE)
        panel.SetBackgroundColour('Black')
        #panel.Freeze()    # Freeze to avoid flickering

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        # Fucked up way to get dateToday with timezone info
        now = datetime.now(pytz.timezone('Europe/Stockholm'))
        #now = datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S') + '+0100', '%Y-%m-%d %H:%M:%S%z')
        dateToday = now.replace(hour=0, minute=0, second=0, microsecond=0)

        weekDays = {0: 'Måndag', 1: 'Tisdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lördag', 6: 'Söndag'}
        weekDays_short = {0: 'mån', 1: 'tis', 2: 'ons', 3: 'tor', 4: 'fre', 5: 'lör', 6: 'sön'}

        # Print out the next X days in detail
        for i in range(0, self.days_to_plot_in_detail):
            currDay = dateToday + timedelta(days=i)
            dayEmpty = True

            # Print heading with current day
            LblDay = wx.StaticText(panel, label="{} {}".format(weekDays[currDay.weekday()], currDay.strftime('%d %b')))
            LblDay.SetForegroundColour('White')
            LblDay.SetFont(self.font_headline)
            sizerMain.Add(LblDay, 1, wx.ALIGN_LEFT, 2)

            # Loop through all events and determine if that event takes place on current day
            for event in self.data.events[0]:
                start = event['start']['dateTime2']
                end = event['end']['dateTime2']
                if start.strftime('%Y-%m-%d') == currDay.strftime('%Y-%m-%d') or (currDay >= start and currDay < end):
                    dayEmpty = False
                    LblEvent = wx.StaticText(panel, label=self.getEventString(event, print_weekday=False))
                    LblEvent.SetFont(self.font_events)
                    if now > start and now < end:
                        LblEvent.SetForegroundColour('White')
                        LblEvent.SetFont(self.font_events_slant)
                    elif now > end:
                        LblEvent.SetForegroundColour('Gray')
                    elif now + timedelta(minutes=30) > start:
                        LblEvent.SetForegroundColour('Red')
                    else:
                        LblEvent.SetForegroundColour('White')

                    sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 0)

            # If day is empty print out a greyed out text with text (nothing)
            if dayEmpty == True:
                LblEvent = wx.StaticText(panel, label=" {}".format('(Ingenting)'))
                LblEvent.SetForegroundColour('Gray')
                LblEvent.SetFont(self.font_events)
                sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 0)

            sizerMain.AddSpacer(10)
        # End day-loop

        # Print out events that takes place later (but within max days)
        currDay = dateToday + timedelta(days=i+1)
        LblDay = wx.StaticText(panel, label="Senare")
        LblDay.SetForegroundColour('White')
        LblDay.SetFont(self.font_headline)
        sizerMain.Add(LblDay, 1, wx.ALIGN_LEFT, 2)
        for event in self.data.events[0]:
            start = event['start']['dateTime2']
            end = event['end']['dateTime2']
            if start >= currDay and start <= dateToday + timedelta(days=self.days_to_plot_total):
                LblEvent = wx.StaticText(panel, label=self.getEventString(event))
                LblEvent.SetForegroundColour('White')
                LblEvent.SetFont(self.font_events)
                sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 0)

        sizerMain.AddSpacer(10)

        # Print out the last updated/created event
        currDay = dateToday + timedelta(days=i + 1)
        LblDay = wx.StaticText(panel, label="Senast uppdaterad")
        LblDay.SetForegroundColour('White')
        LblDay.SetFont(self.font_events)
        sizerMain.Add(LblDay, 1, wx.ALIGN_LEFT, 0)
        for event in self.data.events[2]:
            start = event['start']['dateTime2']
            updated = datetime.strptime(event['updated'], '%Y-%m-%dT%H:%M:%S.%f%z')
            if start >= dateToday and (dateToday - updated).days < 10:
                print(event)
                LblEvent = wx.StaticText(panel, label=self.getEventString(event), style=wx.ALIGN_CENTER_VERTICAL)
                LblEvent.SetForegroundColour('White')
                LblEvent.SetBackgroundColour('Black')
                LblEvent.SetFont(self.font_last_updated)
                sizerMain.Add(LblEvent, 1, wx.ALIGN_LEFT, 0)

        panel.SetSizer(sizerMain)
        panel.Fit()
        self.mainPanel.Fit()

        # panel.Thaw()          # This avoids flickering
        if self.repaint_completely == False:
            self.mainPanel.Thaw()
        else:
            self.repaint_completely == False    # Reset flag

    def updateDataSet(self):
        """
        Updates the data set using the GoogleCalender/GoogleCalender.py -module

        """
        # User input to fetch Google calender data
        self.updated_data = datetime.now()
        self.repaint_completely = True   # Completely repaint
        print('Retrieving data from Google Calender')
        self.data.update()


    def getEventString(self, event, *args, **kwargs):
        # Returns a
        print_weekday = kwargs['print_weekday'] if 'print_weekday' in kwargs else True

        weekDays_short = {0: 'mån', 1: 'tis', 2: 'ons', 3: 'tor', 4: 'fre', 5: 'lör', 6: 'sön'}
        start = event['start']['dateTime2']
        end = event['end']['dateTime2']
        if 'date' in event['start'] and print_weekday == True:
            if (end - start).days == 1:
                datetime_str = '{} {} {}'.format(weekDays_short[start.weekday()], start.day, start.strftime('%b'))
            elif start.month == end.month:
                datetime_str = '{}-{} {}-{} {}'.format(weekDays_short[start.weekday()], weekDays_short[end.weekday()],
                                                       start.day, end.day, start.strftime('%b'))
            else:
                datetime_str = '{}-{} {} {}-{} {}'.format(weekDays_short[start.weekday()], weekDays_short[end.weekday()],
                                                       start.day, start.strftime('%b'), end.day, end.strftime('%b'))
        elif 'date' in event['start'] and print_weekday == False:
            datetime_str = '(1/2)'
        elif print_weekday == False:
            datetime_str = '{}-{}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))
        else:
            datetime_str = '{} {}-{}'.format(weekDays_short[start.weekday()], start.strftime('%H:%M'), end.strftime('%H:%M'))


        return ' {} ({})'.format(event['summary'], datetime_str)

