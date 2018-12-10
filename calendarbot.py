from __future__ import print_function

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import re
import os
import datetime
from dateutil.parser import parse

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

date_time_regex = re.compile('.*?([0-9]{1,2}/[0-9]{1,2}/[0-9]{4}) at ([0-9]{1,2}:[0-9]{2}) to ([0-9]{1,2}:[0-9]{1,2})')

class ChatBot(object):
    def welcome():
        print('\n \n Hello, there! I am your very personal Google calendar Bot!\
        \nYou can ask me different questions about your past and upcoming events.\
        \nBelow is a list of services I could provide \n ... \n')
    welcome()

    def DateTimeReader(self,query_string):
        """
        Parameters- Inputs:
        query_string: query_string

        """
        #this is a method that takes in a query string and spit out a lists of ints that can be manipulated for later usage
        match = date_time_regex.match(query_string)
        if match:
            date = match.group(1)
            start = match.group(2)
            end = match.group(3)
            #print(date, start, end)
            date_split = date.split('/')
            # ['10', '02', '19x
            # [month, day, year]
            start_split = start.split(':')
            end_split = end.split(':')
            # 3:00 -> ['3', '00']
            #print(date_split)



            date_secs = datetime.date(int(date_split[2]), int(date_split[0]), int(date_split[1]))
            start_secs = datetime.time(hour=int(start_split[0]), minute=int(start_split[1]))
            end_secs = datetime.time(hour=int(end_split[0]), minute=int(end_split[1]))

            start_time = datetime.datetime.combine(date_secs, start_secs)
            end_time = datetime.datetime.combine(date_secs, end_secs)

            #print(start_time)
            #print(end_time)

            UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
            start_utc = start_time + UTC_OFFSET_TIMEDELTA
            end_utc = end_time + UTC_OFFSET_TIMEDELTA

            start_utc = start_utc.isoformat() + 'Z'
            end_utc = end_utc.isoformat() + 'Z'

            return [start_utc,end_utc]


        else:
            print('bad format!')
            print('Correct format : [phrases] month/day/yr at sh:sm to eh:em, (military time format)')

    def avaibility_checker(self,ask_what_time_period): #check if user is available or not in the given time period
        """
        Parameters- Inputs:
        query_string: query_string
        ask_what_time_period: import string

        """
        time = self.DateTimeReader(ask_what_time_period)
        start_utc = time[0]
        end_utc = time[1]
        events_result = self.service.events().list(calendarId='primary', timeMin=start_utc,
                                            timeMax = end_utc,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if len(events) >= 1:
            print('\n Not Available\n User is busy in the given time period, please try again with a different time range.')
        else:
            print('\n Available\n User is available!')



    def __init__(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('calendar', 'v3', http=creds.authorize(Http()))

    def query(self, query_string):  #I had remodifiy this code from Google Calendar API's quickstart code. You can see the original code in my requirement.txt"
        """
        Parameters- Inputs:
        query_string: query_string

        """
        # this function will read the time from the Chatbot
        # format the time into the format of the now variable
        # service.events().list()
        match = date_time_regex.match(query_string)
        if match:
            date = match.group(1)
            start = match.group(2)
            end = match.group(3)
            #print(date, start, end)
            date_split = date.split('/')
            # ['10', '02', '19']
            # [month, day, year]
            start_split = start.split(':')
            end_split = end.split(':')
            # 3:00 -> ['3', '00']
            #print(date_split)
            #print(end_split)

            date_secs = datetime.date(int(date_split[2]), int(date_split[0]), int(date_split[1]))
            start_secs = datetime.time(hour=int(start_split[0]), minute=int(start_split[1]))
            end_secs = datetime.time(hour=int(end_split[0]), minute=int(end_split[1]))

            #print(date_secs,start_secs,end_secs)

            start_time = datetime.datetime.combine(date_secs, start_secs)
            end_time = datetime.datetime.combine(date_secs, end_secs)

            #print(start_time)
            #print(end_time)

            UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
            start_utc = start_time + UTC_OFFSET_TIMEDELTA
            end_utc = end_time + UTC_OFFSET_TIMEDELTA
            start_utc = start_utc.isoformat() + 'Z'
            end_utc = end_utc.isoformat() + 'Z'

            #print(start_utc)
            #print(end_utc)
            #now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(calendarId='primary', timeMin=start_utc,
                                                timeMax =end_utc,
                                                maxResults=10, singleEvents=True,# XXX:
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            event_list = []

            if not events:
                print('No upcoming events found. User is free :)')
            for event in events:
                #number_of_events = event.count()
                #print('There are',number_of_events, 'events in this time slot')
                start = event['start']['dateTime']
                end = event['end']['dateTime']
            #    print(start, event['summary'])
                #print(type(start))
                # print(type(event['start']['dateTime']))
                # print(event['start'])

                #2018-11-26T07:30:00-08:00
                start = parse(start).strftime('%m-%d-%Y at %H:%M:%S')
                end = parse(end).strftime('%m-%d-%Y at %H:%M:%S')
                #print(start, end,event['summary'])
                event_list.append((start, end, event['summary']))

            # print entire list
            for start, end, summary in event_list:
                print(f'{start} to {end}: {summary}')

            print("\n Press 'e' to export this scheudle summary as a .txt file on your desktop.")
            x = input('\n Enter e or press Enter key to ignore: \n')  #a sub function where it will generate a textfile from the scheudle I pulled from google calendar api
            if x == "e":
                with open('Yourschedule.txt', 'w+') as output:
                    for start, end, summary in event_list:
                        output.write(f'{start} to {end}: {summary}\n')
                print("\n You will be able to find the text file 'Yourschedule' under the same folder as this program.")    #Still need to fix this so when user uses this command again it will overwrite the whole text file




    #def avaibility(,)

        else:
            print('bad format!')
            print('Correct format : [phrases] month/day/yr at sh:sm to eh:em, (military time format)')




# specify a date range
# i.e. free on 10/2/2019 at 14:00 to 15:00
#   mon/date/year at sh:sm - eh:em
'''

'''
if __name__ == '__main__':
    c = ChatBot()
    while True:
        x = input("\n Main Function List:\n\
        Enter ‘show' or 's’ to see one’s schedule in the indicated time range.\n\
        Enter ‘availability' or 'a’ to check if one is available or not in the indicated time range.\n\
        Enter 'f' to show RESPECT \n\
        Or\n\
        Enter ‘q’ to quit.\n")



        #"Enter a time with the format exampple: (11/26/2018 at 7:00 to 13:00),\n enter 'availability' to check if one is free during certi
        if x == 'show' or x == 's':
            time = input('  Please provide the time slot range you desire to see with the format example of (11/26/2018 at 7:00 to 13:00)\n\
        \n  **Please take in consideration that your input date and time must be reasonable** \n Your time: ')
            c.query(time) #show all the google Calenar tasks

        elif x ==  'availability' or x == 'a':
            time = input('Please provide the time slot range you desire to know if one is available or not with the format example of (11/26/2018 at 7:00 to 13:00)\n\
        \n  **Please take in consideration that your input date and time must be reasonable** \n Your time: ')
            c.avaibility_checker(time)

        elif x == 'f':
            print('\
                    _____  ______  _____ _____  ______ _____ _______ \n\
                   |  __ \|  ____|/ ____|  __ \|  ____/ ____|__   __| \n\
                   | |__) | |__  | (___ | |__) | |__ | |       | |   \n\
                   |  _  /|  __|  \___ \|  ___/|  __|| |       | |   \n\
                   | | \ \| |____ ____) | |    | |___| |____   | |   \n\
                   |_|  \_\______|_____/|_|    |______\_____|  |_|   \n\
                                                  ')

        #if x == 'quick' or x == 'q':
        #if x == 'new':
        elif x == 'q':
            break # quit
        else:
            print('\n Please enter one of the listed commands, thank you! :) \n')  #Need to fix this, it would still pop up after
    #c.avaibility_checker(ask_what_time_period)
