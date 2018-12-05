import requests
import base64
from datetime import datetime
from datetime import timedelta
from operator import itemgetter


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

        serverDateTime = datetime.strptime(tmp['DepartureBoard']['serverdate'] + ' ' + tmp['DepartureBoard']['servertime'], "%Y-%m-%d %H:%M")
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

