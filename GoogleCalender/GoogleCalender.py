from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from operator import itemgetter

from datetime import datetime
from datetime import timedelta

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


class GoogleCalender:

    def __init__(self, credentials_filename, token_filenames, *args, **kwargs):
        if not isinstance(token_filenames, list):
            self.token_filenames = [token_filenames]
        else:
            self.token_filenames = token_filenames
        if 'apa' in kwargs:
            test=0

        self.credentials_filename = credentials_filename
        self.events = []
        self.update()

    def _getDateObject(self, str):
        # Input:    str    Datetime in the form YYYY-MM-DDTHH:MM:SS+XX:XX
        # Output    datetime object with correct timezone
        str = str[:len(str)-3] + str[-2:]
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S%z')

    def update(self):
        self.events = [[], [], []]
        for i in range(0,len(self.token_filenames)):
            store = file.Storage(self.token_filenames[i])
            creds = store.get()

            if not creds or creds.invalid:
                flow = client.flow_from_clientsecrets(self.credentials_filename, SCOPES)
                creds = tools.run_flow(flow, store)
            service = build('calendar', 'v3', http=creds.authorize(Http()))

            # Call the Calendar API
            now = datetime.now()
            today = now.strftime('%Y-%m-%dT') + '00:00:00+01:00'

            for j in range(0, 3):
                if j == 0:
                    events_result = service.events().list(calendarId='primary', timeMin=today, maxResults=100,
                                                          singleEvents=True, orderBy='startTime').execute()
                elif j == 1:
                    events_result = service.events().list(calendarId='primary', timeMin=today, maxResults=100,
                                                          singleEvents=False).execute()
                elif j == 2:
                    events_result = service.events().list(calendarId='primary', timeMin=today, maxResults=100,
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
                    self.events[j].append(event)

                    #self.events[j].extend(events)

        # Sort list
        self.status_ok = True

        self.events[0] = sorted(self.events[0], key=itemgetter('dateTimeStart'), reverse=False)
        self.events[1] = sorted(self.events[1], key=itemgetter('dateTimeStart'), reverse=False)
        self.events[2] = sorted(self.events[2], key=itemgetter('updated'), reverse=True)


def main():

    newCal = GoogleCalender('credentials.json', ['Calender_shared.json', 'Calender_personal.json'])
    for i in range(0,len(newCal.events)):
        print(newCal.events[i]['summary'], ' startar', newCal.events[i]['start']['dateTime2'].hour)
        if 'date' in newCal.events[i]['start']:
            print(newCal.events[i]['summary'], ' startar', newCal.events[i]['start']['date'], '(heldagsaktivitet)')
        else:
            print(newCal.events[i]['summary'], ' startar', newCal.events[i]['start']['dateTime'])




if __name__ == '__main__':
    main()