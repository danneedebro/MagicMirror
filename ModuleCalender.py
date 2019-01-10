"""
Graphic module for Google Calender data

"""

#   -----------------------------
#   |Today                      |
#   -----------------------------
#   |Entry                      |
#   -----------------------------
#   -----------------------------


# FIXA så att man kan ge en dict med de kalendrar man vill se.
# Ex  [{'Id':'danielochsofia@gmail.com', 'token-file':'token1.json', 'color': 'red', 'recurring': True

from datetime import datetime
from datetime import timedelta
import wx
import GoogleCalender.GoogleCalender
import pytz


class ModuleCalender:
    weekDays = {0: 'Måndag', 1: 'Tisdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag', 5: 'Lördag', 6: 'Söndag'}
    timezone = pytz.timezone('Europe/Stockholm')

    def __init__(self, panel_main, calendars_input, **kwargs):
        """
        Constructor. Creates a graphical module to display Google Calender data

        Args:
            panel_main:                  wx.Panel object for the container/panel that holds the other widgets
            update_freq_graphics (int): Time in seconds between updates of the graphical module
            update_freq_data (int):     Time in seconds between fetching data from Google

        """

        self.panel_main = panel_main
        self.caledars_input = calendars_input

        self.update_freq_graphics = kwargs['update_freq_graphics'] if 'update_freq_graphics' in kwargs else 30
        self.update_freq_data = kwargs['update_freq_data'] if 'update_freq_data' in kwargs else 60
        self.days_to_plot_in_detail = kwargs['days_to_plot_in_detail'] if 'days_to_plot_in_detail' in kwargs else 7
        self.days_to_plot_total = kwargs['days_to_plot_total'] if 'days_to_plot_total' in kwargs else 14

        self.repaint_completely = False   # Flag to fix problem with text residues. Causes som flicker so it's best to
                                          # only set this to flag True when dataset is refreshed

        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()
        self.font1 = wx.Font(pointSize=14, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL)
        self.font2 = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL)
        self.font3 = wx.Font(pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.SLANT,
                             weight=wx.FONTWEIGHT_NORMAL)
        self.font4 = wx.Font(pointSize=9, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL,
                             weight=wx.FONTWEIGHT_NORMAL)
        credentials_filename = 'GoogleCalender/credentials.json'
        #token_filenames = ['GoogleCalender/Calender_shared.json', 'GoogleCalender/Calender_personal.json']
        self.data = GoogleCalender.GoogleCalender.GoogleCalender(credentials_filename, calendars_input)

        self.update_dataset()
        self.update_graphics()

    def update_check(self):
        if (datetime.now() - self.updated_data).total_seconds() > self.update_freq_data:
            self.update_dataset()

        if (datetime.now() - self.updated_graphics).total_seconds() > self.update_freq_graphics:
            self.update_graphics()

    def update_graphics(self):
        """
        Updates the graphics

        Step 1. Delete all objects in panel_main
        Step 2. Creates StaticText objects that are added to a boxsizer (Vertical)

        """
        now = datetime.now()
        self.updated_graphics = now
        if self.repaint_completely is False:
            self.panel_main.Freeze()   # Freeze to avoid flickering

        # Delete all objects in main container for this module
        for myobj in self.panel_main.GetChildren():
            myobj.DestroyChildren()
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.panel_main, style=wx.EXPAND | wx.ALIGN_CENTER | wx.FULL_REPAINT_ON_RESIZE)
        panel.SetBackgroundColour('Black')
        # panel.Freeze()    # Freeze to avoid flickering

        sizer_main = wx.BoxSizer(wx.VERTICAL)

        # Fucked up way to get date_today with timezone info
        now = datetime.now(self.timezone)
        date_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Print out the next X days in detail
        for i in range(0, self.days_to_plot_in_detail):
            curr_day = date_today + timedelta(days=i)
            day_empty = True

            # Print heading with current day
            lbl_day = wx.StaticText(panel, label="{} {}".format(self.weekDays[curr_day.weekday()],
                                                                curr_day.strftime('%d %b')))
            lbl_day.SetForegroundColour('White')
            lbl_day.SetFont(self.font1)
            sizer_main.Add(lbl_day, 1, wx.ALIGN_LEFT, 2)

            # Loop through all events and determine if that event takes place on current day
            for event in self.data.events[0]:
                start = event['start']['dateTime2']
                end = event['end']['dateTime2']
                if start.strftime('%Y-%m-%d') == curr_day.strftime('%Y-%m-%d') or (start <= curr_day < end):
                    day_empty = False
                    lbl_event = wx.StaticText(panel, label=event['summary'])
                    lbl_event.SetFont(self.font2)
                    lbl_time = wx.StaticText(panel, label=ModuleCalender.getEventString(event, print_weekday=False, only_time=True))
                    lbl_time.SetForegroundColour('Grey')
                    lbl_time.SetFont(self.font2)
                    if start < now < end:
                        lbl_event.SetForegroundColour('White')
                        lbl_event.SetFont(self.font3)
                    elif now > end:
                        lbl_event.SetForegroundColour('Gray')
                    elif now + timedelta(minutes=30) > start:
                        lbl_event.SetForegroundColour('Red')
                    else:
                        lbl_event.SetForegroundColour('White')

                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    sizer.Add(lbl_event, 0, wx.ALIGN_CENTER_VERTICAL, 0)
                    sizer.Add(lbl_time, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
                    sizer_main.Add(sizer, 1, wx.ALIGN_LEFT, 0)

            # If day is empty print out a greyed out text with text (nothing)
            if day_empty is True:
                lbl_event = wx.StaticText(panel, label=" {}".format('(Ingenting)'))
                lbl_event.SetForegroundColour('Gray')
                lbl_event.SetFont(self.font2)
                sizer_main.Add(lbl_event, 1, wx.ALIGN_LEFT, 0)

            sizer_main.AddSpacer(10)
        # End day-loop

        # Print out events that takes place later (but within max days)
        curr_day = date_today + timedelta(days=i+1)
        lbl_day = wx.StaticText(panel, label="Senare")
        lbl_day.SetForegroundColour('White')
        lbl_day.SetFont(self.font1)
        sizer_main.Add(lbl_day, 1, wx.ALIGN_LEFT, 2)
        for event in self.data.events[0]:
            start = event['start']['dateTime2']
            if curr_day <= start <= date_today + timedelta(days=self.days_to_plot_total):
                lbl_event = wx.StaticText(panel, label=event['summary'])
                lbl_event.SetForegroundColour('White')
                lbl_event.SetFont(self.font2)
                lbl_time = wx.StaticText(panel, label=ModuleCalender.getEventString(event, only_time=True))
                lbl_time.SetForegroundColour('Grey')
                lbl_time.SetFont(self.font4)
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(lbl_event, 0, wx.ALIGN_CENTER_VERTICAL, 0)
                sizer.Add(lbl_time, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
                sizer_main.Add(sizer, 1, 0, 0)

        sizer_main.AddSpacer(10)

        # Print out the last updated/created event
        lbl_day = wx.StaticText(panel, label="Senast uppdaterad")
        lbl_day.SetForegroundColour('White')
        lbl_day.SetFont(self.font2)
        sizer_main.Add(lbl_day, 1, wx.ALIGN_LEFT, 0)
        for event in self.data.events[2]:
            start = event['start']['dateTime2']
            updated = datetime.strptime(event['updated'][0:-1]+'+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
            if start >= date_today and (date_today - updated).days < 10:
                lbl_event = wx.StaticText(panel, label=event['summary'])
                lbl_event.SetForegroundColour('White')
                lbl_event.SetBackgroundColour('Black')
                lbl_event.SetFont(self.font4)
                lbl_time = wx.StaticText(panel, label=ModuleCalender.getEventString(event, only_time=True))
                lbl_time.SetForegroundColour('Grey')
                lbl_time.SetBackgroundColour('Black')
                lbl_time.SetFont(self.font4)
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(lbl_event, 0, wx.ALIGN_CENTER_VERTICAL, 0)
                sizer.Add(lbl_time, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
                sizer_main.Add(sizer, 1, wx.ALIGN_LEFT, 0)

        panel.SetSizer(sizer_main)
        panel.Fit()
        self.panel_main.Fit()

        # panel.Thaw()          # This avoids flickering
        if self.repaint_completely is False:
            self.panel_main.Thaw()
        else:
            self.repaint_completely = False    # Reset flag

    def update_dataset(self):
        """
        Updates the data set using the GoogleCalender/GoogleCalender.py -module

        """
        # User input to fetch Google calender data
        self.updated_data = datetime.now()
        self.repaint_completely = True   # Completely repaint
        print('Retrieving data from Google Calender')
        self.data.update()

    @staticmethod
    def getEventString(event, **kwargs):
        # Returns a formatted string for the date and time depending on type of event. There are six main types
        #    1. Whole day event within the 'zoomed' date span. Should return "Event 1/1"
        #    2. Whole day event outside the 'zoomed' date span. Should return "Event tue 3 Jan"
        #    3. Multiple day event whithin the 'zoomed' date span. Should return "Event X/3"
        #    4. Multiple day event outside the 'zoomed' date span. Should return "Event mon-wed 1 jan-3 jan"
        #    5. Time event within the 'zoomed' date span. Should return "Event 11:30-12:30"
        #    6. Time event outside the 'zoomed' date span. Should return "Event mån 3 jan 11:30-12:30"
        print_weekday = kwargs['print_weekday'] if 'print_weekday' in kwargs else True
        only_time = kwargs['only_time'] if 'only_time' in kwargs else False
        weekdays_short = {0: 'mån', 1: 'tis', 2: 'ons', 3: 'tor', 4: 'fre', 5: 'lör', 6: 'sön'}

        start = event['start']['dateTime2']
        end = event['end']['dateTime2']
        if 'date' in event['start'] and print_weekday is True:
            if (end - start).days == 1:
                datetime_str = '{} {} {}'.format(weekdays_short[start.weekday()], start.day, start.strftime('%b'))
            elif start.month == end.month:
                datetime_str = '{}-{} {}-{} {}'.format(weekdays_short[start.weekday()],
                                                       weekdays_short[end.weekday()],
                                                       start.day, end.day, start.strftime('%b'))
            else:
                datetime_str = '{}-{} {} {}-{} {}'.format(weekdays_short[start.weekday()],
                                                          weekdays_short[end.weekday()],
                                                          start.day, start.strftime('%b'), end.day, end.strftime('%b'))
        elif 'date' in event['start'] and print_weekday is False:
            datetime_str = '(1/2)'
        elif print_weekday is False:
            datetime_str = '{}-{}'.format(start.strftime('%H:%M'), end.strftime('%H:%M'))
        else:
            datetime_str = '{} {} {} {}-{}'.format(weekdays_short[start.weekday()], start.day,
                                                   start.strftime('%b'), start.strftime('%H:%M'), end.strftime('%H:%M'))

        if only_time:
            return '{}'.format(datetime_str)
        else:
            return ' {} ({})'.format(event['summary'], datetime_str)
