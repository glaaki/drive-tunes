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

LOCAL_SAVE_PATH = 'Music'
PHONE_SAVE_PATH = ''

try:
    spreadsheet_id = os.environ['TUNES_SHEET_ID']
except KeyError:
    raise KeyErrror('Please set the TUNES_SHEET_ID env variable with your google sheet id.')

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
    successful_tracks, failed_tracks = download_tracks(song_data)
    main_tab_data = pad_sheet_data(failed_tracks, len(song_data))
    append_to_sheet('Previously Downloaded!A2:D', successful_tracks)
    update_sheet('Song Data!A2:D', main_tab_data)
    if failed_tracks:
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
    successes = []
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
            successes.append(song)
        except:
            failures.append(song)
    return (successes, failures)


# albums and artists make up part of the path, but occasionally there are characters
# that cause windows to throw a fit. this is not meant to be a robust solution to path
# sanitization, just catching the obvious things.
def create_safe_path(artist, album):
    windows_reserved_path_chars = ['<','>',':','"','/', '\\','|','?','*']
    for unsafe_char in windows_reserved_path_chars:
        artist = artist.replace(unsafe_char, '')
        album = album.replace(unsafe_char, '')
    return os.path.join(LOCAL_SAVE_PATH, artist, album)


def update_sheet(range_name, values):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    body = {'values': values}
    result = service.spreadsheets().values().update(
             spreadsheetId=spreadsheet_id, range=range_name,
             valueInputOption='RAW', body=body).execute()


def append_to_sheet(range_name, values):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    body = {'values': values}
    result = service.spreadsheets().values().append(
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
    """Parses the auth json we store in env and creates OAuth2Credentials.

    Returns:
        Credentials, the obtained credential.
    """
    if 'GOOGLE_AUTH_JSON' in os.environ:
        return client.OAuth2Credentials.from_json(os.environ['GOOGLE_AUTH_JSON'])
    else:
        raise EnvironmentError('GOOGLE_AUTH_JSON env not set. did you run the setup ansible?')


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
