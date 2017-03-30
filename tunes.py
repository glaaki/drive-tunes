#!/usr/bin/env python


from __future__ import unicode_literals, print_function
import httplib2
import os
import youtube_dl

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
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive Tunes'
LOCAL_SAVE_PATH = 'Music'
PHONE_SAVE_PATH = ''

options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': "mp3",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True
}


def main():
    song_data = get_song_list()
    failed_downloads = download_tracks(song_data)
    print('The following tracks errored out and were not obtained:')
    for fail in failed_downloads:
        print(fail)


# download the youtube videos, returns the strings of the
# failed tracks for manual intervention by the user.
def download_tracks(song_list):
    failures = []
    for song in song_list:
        artist = song[0]
        track_name = song[1]
        album = song[2] # this might be '', but the joins below handle it
        url = song[3]
        save_path = os.path.join(LOCAL_SAVE_PATH, artist, album)
        filename = artist + ' - ' + track_name + '.%(ext)s'
        options['outtmpl'] = os.path.join(save_path, filename)
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([url])
        except:
            failures.append(artist + ' - ' + track_name)
    return failures


# connects to google drive and gets our desired track list
def get_song_list():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1w0iR-v-SYYzpznMdEcA94i6MCIiN0VLUE59tGUajlBI'
    rangeName = 'Song Data!A2:D'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    return result.get('values', [])


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


if __name__ == "__main__":
    main()
