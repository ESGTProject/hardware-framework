from __future__ import print_function
import httplib2
import os
import base64
import email
import json
import datetime
import pytz

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at /.credentials/
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
APPLICATION_NAME = 'ESGT Backend'

class Gmail(object):

    def __init__(self, secret_file, credential_path):
        self.secret_file = secret_file
        self.credential_path = credential_path

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        if not os.path.exists(os.path.dirname(self.credential_path)):
            os.makedirs(os.path.dirname(self.credential_path))
        store = Storage(self.credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secret_file, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + self.credential_path)
        return credentials

    def list_messages_with_labels(self, service, user_id, label_ids=[]):
        """List all Messages of the user's mailbox with label_ids applied.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            label_ids: Only return Messages with these labelIds applied.

        Returns:
            List of Messages that have all required Labels applied. Note that the
            returned list contains Message IDs, you must use get with the
            appropriate id to get the details of a Message.
        """
        try:
            response = service.users().messages().list(userId=user_id,
                                                    labelIds=label_ids).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id,
                                                        labelIds=label_ids,
                                                        pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except errors.HttpError, error:
            print ('An error occurred: %{}'.format(error))

    def get_message(self, service, user_id, msg_id):
        """Get a Message with given ID.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: The ID of the Message required.

        Returns:
            A Message.
        """
        try:
            return service.users().messages().get(userId=user_id, id=msg_id).execute()
        except errors.HttpError, error:
            print('An error occurred: {}'.format(error))


    def get_message_with_mime(self, service, user_id, msg_id):
        """Get a Message and use it to create a MIME Message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: The ID of the Message required.

        Returns:
            A MIME Message, consisting of data from Message.
        """
        try:
            message = service.users().messages().get(userId=user_id, id=msg_id,
                                                    format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            mime_msg = email.message_from_string(msg_str)
            return mime_msg
        except errors.HttpError, error:
            print('An error occurred: {}'.format(error))

    def get_inbox_messages(self, service, user_id):
        """Gets list of messages in inbox

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.

        Returns:
            List of message objects
        """

        message_id_list = self.list_messages_with_labels(service, user_id, label_ids=['INBOX'])
        message_list = []
        if message_id_list is not None:
            for id_dict in message_id_list:
                message_content = self.get_message(service, user_id, id_dict[u'id'])
                message_list.append(message_content)
            return message_list
        else:
            print('No messages found.')
            return None

    def simplify_message(self, message):
        """ Simplifies message to get essential information

        Args:
            message: Message dictionary retrieved using Google API

        Returns:
            Simplified message dictionary object

        """
        headers = message['payload']['headers']

        simplified_message = {
            'timestamp' : pytz.utc.localize(datetime.datetime.fromtimestamp(long(message['internalDate'])/1000), is_dst=None).astimezone(pytz.utc),
            'from' : filter(lambda header: header['name'] == 'From', headers)[0]['value'],
            'subject' : filter(lambda header: header['name'] == 'Subject', headers)[0]['value'],
            'content' : message['snippet']
        }

        return simplified_message
    def get_json(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)

        messages = self.get_inbox_messages(service, "me")
        if messages is not None:
            return list(map(self.simplify_message, messages))
        else:
            print('Failed to retrieve message')

def main():
    gmail_api = Gmail('gmail_client_secret.json','./.credentials/gmail-session.json')
    print (gmail_api.get_json())

if __name__ == "__main__":
    main()
