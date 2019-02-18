"""
Fetches events from one or more Google calendar

Args:
    credentials_file: (str)     A credentials file downloaded from Google APIs console
    calendars: (dict)           An input dict containing information about the calendars to be read

Output:
    self.events[0]: (dict)      Sorted dict with ALL events from all calendars in 'calendars'
    self.events[1]: (dict)      Sorted dict with UNIQUE/non-recurring events from all calendars in 'calendars'
    self.events[2]: (dict)      Sorted dict by 'udated' keyword with UNIQUE/non-recurring events from all calendars in 'calendars'

    self.status_ok: (bool)      True if ok

calendars dict example
{
    'Calendar - primary': {'id': 'primary', 'tokenFile': '<filename>', 'maxResults': 100, 'trackUpdates': True},
    'Calendar - birthdays': {'id': '#contacts@group.v.calendar.google.com', 'tokenFile': '<filename>', 'maxResults': 100, 'trackUpdates': False}
}
id:             ex: 'primary', 'john.smith@gmail.com'
tokenFile:      ex: 'token1.json'
trackUpdates:   If TRUE fetch events with orderBy='updated' for this calendar 

"""


from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from operator import itemgetter

from datetime import datetime
from datetime import timedelta
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

# Url where credentials file easily can be created
url_help = 'https://developers.google.com/calendar/quickstart/python'


class GoogleCalender:

    timezone = pytz.timezone('Europe/Stockholm')

    def __init__(self, credentials_filename, calendars_input, *args, **kwargs):

        self.calendars_input = calendars_input

        # Check to see if credentials_filename exists
        try:
            fh = open(credentials_filename, 'r')
            # Store configuration file values

            self.credentials_filename = credentials_filename
            self.events = []
            self.update()

        except FileNotFoundError:
            print('Error: {} doesn\'t exist. Create one at Google APIs console or here: {}'.format(credentials_filename, url_help))
            self.status_ok = False
            return

        

    def _getDateObject(self, str):
        # Input:    str    Datetime in the form YYYY-MM-DDTHH:MM:SS+XX:XX
        # Output    datetime object with correct timezone
        str = str[:len(str)-3] + str[-2:]
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S%z')

    def update(self):
        self.events = [[], [], []]

        for calendar_tag, calendar in self.calendars_input.items():
            token_file = calendar['tokenFile']
            max_results = calendar['maxResults'] if 'maxResults' in calendar else 100
            calendar_id = calendar['id'] if 'id' in calendar else 'primary'
            track_updates = calendar['trackUpdates'] if 'trackUpdates' in calendar else True
            days_ahead = calendar['daysAhead'] if 'daysAhead' in calendar else 0

            store = file.Storage(token_file)
            creds = store.get()

            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(self.credentials_filename, SCOPES)
                creds = tools.run_flow(flow, store)
            service = build('calendar', 'v3', http=creds.authorize(Http()))

            # Call the Calendar API
            #now = datetime.now()
            now = self.timezone.localize(datetime.now())
            date_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            date_stop = date_today + timedelta(days=days_ahead)
            strToday = date_today.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            strDaysAhead = date_stop.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            print(strDaysAhead)
            
            

            for j in range(0, 3):
                print('Läser in {} från tokenFile={}, index={}'.format(calendar_id, token_file, j))
                if j == 0:
                    if days_ahead > 0:
                        events_result = service.events().list(calendarId=calendar_id, timeMin=strToday, timeMax=strDaysAhead, maxResults=max_results,
                                                          singleEvents=True, orderBy='startTime').execute()
                    else:
                        events_result = service.events().list(calendarId=calendar_id, timeMin=strToday, maxResults=max_results,
                                                          singleEvents=True, orderBy='startTime').execute()
                elif j == 1:
                    events_result = service.events().list(calendarId=calendar_id, timeMin=strToday, maxResults=max_results,
                                                          singleEvents=False).execute()
                
                elif j == 2:   
                    if track_updates is False:
                        break
                    events_result = service.events().list(calendarId=calendar_id, timeMin=strToday, maxResults=max_results,
                                                          singleEvents=False, orderBy='updated').execute()

                events = events_result.get('items', [])

                if not events:
                    print('Info ' + now.strftime('(%Y-%m-%d %H:%M): ') + 'No upcoming events found')

                # Loop through events and add a dateTime object in current event called 'dateTimeStart' and 'dateTimeEnd'
                for event in events:
                    if 'date' in event['start']:    # if whole-day activity
                        event['start']['dateTime2'] = datetime.strptime(event['start']['date'] + ' +0100', '%Y-%m-%d %z')
                        event['end']['dateTime2'] = datetime.strptime(event['end']['date']+ ' +0100', '%Y-%m-%d %z')
                        event['dateTimeStart'] = event['start']['dateTime2'].strftime('%Y-%m-%d %H:%M:%S')
                    elif 'dateTime' in event['start']:   # If
                        event['start']['dateTime2'] = self._getDateObject(event['start']['dateTime'])
                        event['end']['dateTime2'] = self._getDateObject(event['end']['dateTime'])
                        event['dateTimeStart'] = event['start']['dateTime2'].strftime('%Y-%m-%d %H:%M:%S')

                for event in events:
                    if 'summary' not in event:
                        event['summary'] = '(Ingen titel)'
                    #print('   {} start={}, updated={}'.format(event['summary'], event['start'], event['updated']))
                    #print(event)
                    self.events[j].append(event)


        # Sort list
        self.status_ok = True

        self.events[0] = sorted(self.events[0], key=itemgetter('dateTimeStart'), reverse=False)
        self.events[1] = sorted(self.events[1], key=itemgetter('dateTimeStart'), reverse=False)
        self.events[2] = sorted(self.events[2], key=itemgetter('updated'), reverse=True)


def initiateAuthProcess():
    print('This creates a json-file containing tokens to')
    file_credentials = input('Credentials filename: ')
    file_token = input('Desired token filename: ')
    calendar = {'Calendar-tag':{'id': 'primary', "tokenFile": file_token, "maxResults": 1, "trackUpdates": False}}
    GC = GoogleCalender(file_credentials, calendar)
    if GC.status_ok is True:
        print('Everything is OK')
    else:
        print('Something went wrong')


if __name__ == '__main__':
    initiateAuthProcess()