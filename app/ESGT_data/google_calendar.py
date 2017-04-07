from __future__ import print_function
import httplib2
import os
import base64
import email
import json
import datetime
import pytz

from apiclient import discovery
from apiclient import errors


class GoogleCalendar(object):
    def __init__(self):
        pass

    def get_upcoming_events(self, service):
        """Gets list of upcoming events in calendar

        Args:
            service: Authorized Google Calendar service instance.

        Returns:
            List of event objects
        """
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        try:
            eventsResult = service.events().list(
                calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
            events = eventsResult.get('items', [])
            return events
        except errors.HttpError as error:
            print('An error occurred: {}'.format(error))
            return None

    def simplify_events(self, event):
        """ Simplifies google calendar event to get essential information

        Args:
            event: Event dictionary retrieved using Google API

        Returns:
            Simplified event dictionary object

        """
        print(event)
        simplified_event = {
            #'timestamp' : pytz.utc.localize(datetime.datetime.fromtimestamp(int(message['internalDate'])/1000), is_dst=None).astimezone(pytz.utc),
            'summary' : event['summary'],
            'start' : event['start']['dateTime'] if 'dateTime' in event['start'] else event['start']['date'],
            'end' : event['end']['dateTime'] if 'dateTime' in event['end'] else event['end']['date'],
            'created' : event['created'],
            'updated' : event['updated']
        }
        return simplified_event

    def get_json(self, credentials):
        """Get json list of upcoming calendar events

        Arguments:
            credentials : Credential object for authorizing access to calendar API
        """
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        events = self.get_upcoming_events(service)
        print (events)

        if events is not None:
            return list(map(self.simplify_events, events))
        else:
            print('Failed to retrieve events')
