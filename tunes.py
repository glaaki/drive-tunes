#!/usr/bin/env python


from __future__ import unicode_literals, print_function
import httplib2
import os
import sys
import youtube_dl
from youtube_dl.postprocessor.ffmpeg import FFmpegMetadataPP

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
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive Tunes'
LOCAL_SAVE_PATH = 'Music'
PHONE_SAVE_PATH = ''

try:
    spreadsheet_id = os.environ['TUNES_SHEET_ID']
except KeyError:
    print('Please set the TUNES_SHEET_ID env variable with your google sheet id.')
    sys.exit()

options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': "mp3",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'noplaylist': True
}


def main():
    song_data = get_song_list()
    failed_downloads = download_tracks(song_data)
    new_sheet_data = pad_sheet_data(failed_downloads, len(song_data))
    update_sheet(new_sheet_data)
    if failed_downloads:
        print('\nThe following tracks errored out and were not obtained:')
        for fail in failed_downloads:
            print(fail[0] + ' - ' + fail[1])


# takes the failed entries and adds blank rows until it's the
# same length as the original data (that way when we write it
# back, it has the effect of clearing everything but the errors)
def pad_sheet_data(rows_to_keep, row_count):
    padded_data = rows_to_keep[:]
    while len(padded_data) < row_count:
        padded_data.append(['', '', '', ''])
    return padded_data


# download the youtube videos, returns the failed tracks
def download_tracks(song_list):
    failures = []
    for song in song_list:
        artist = song[0].strip()
        track_name = song[1].strip()
        album = song[2].strip() # this might be '', but the joins below handle it
        url = song[3].strip()
        save_path = create_safe_path(artist, album)
        filename = artist + ' - ' + track_name + '.%(ext)s'
        options['outtmpl'] = os.path.join(save_path, filename)
        metadata = {
            'title': track_name,
            'artist': artist,
            'album': album,
        }
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                ffmpeg_mp3_metadata_pp = FFmpegMP3MetadataPP(ydl, metadata)
                ydl.add_post_processor(ffmpeg_mp3_metadata_pp)
                ydl.download([url])
        except:
            failures.append(song)
    return failures


# albums and artists make up part of the path, but occasionally there are characters
# that cause windows to throw fit. this is not meant to be a robust solution to path
# sanitization, just catching the obvious things.
def create_safe_path(artist, album):
    windows_reserved_path_chars = ['<','>',':','"','/', '\\','|','?','*']
    for unsafe_char in windows_reserved_path_chars:
        artist = artist.replace(unsafe_char, '')
        album = album.replace(unsafe_char, '')
    return os.path.join(LOCAL_SAVE_PATH, artist, album)


def update_sheet(values):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    range_name = 'Song Data!A2:D'
    body = {'values': values}
    result = service.spreadsheets().values().update(
             spreadsheetId=spreadsheet_id, range=range_name,
             valueInputOption='RAW', body=body).execute()


# connects to google drive and gets our desired track list
def get_song_list():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    rangeName = 'Song Data!A2:D'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=rangeName).execute()
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


# https://github.com/rg3/youtube-dl/issues/12225
# youtube-dl will only add metadata if it infers the data by itself.
# here is a custom postprocessor to add the title / album we specify.
class FFmpegMP3MetadataPP(FFmpegMetadataPP):

    def __init__(self, downloader=None, metadata=None):
        self.metadata = metadata or {}
        super(FFmpegMP3MetadataPP, self).__init__(downloader)

    def run(self, information):
        information = self.purge_metadata(information)
        information.update(self.metadata)
        return super(FFmpegMP3MetadataPP, self).run(information)

    def purge_metadata(self, info):
        info.pop('title', None)
        info.pop('track', None)
        info.pop('upload_date', None)
        info.pop('description', None)
        info.pop('webpage_url', None)
        info.pop('track_number', None)
        info.pop('artist', None)
        info.pop('creator', None)
        info.pop('uploader', None)
        info.pop('uploader_id', None)
        info.pop('genre', None)
        info.pop('album', None)
        info.pop('album_artist', None)
        info.pop('disc_number', None)
        return info


if __name__ == "__main__":
    main()
