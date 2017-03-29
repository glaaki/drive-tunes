#!/usr/bin/env python


from __future__ import unicode_literals
from selenium import webdriver
import youtube_dl


def make_video_list(user, pswd):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://keep.google.com/')
    username_field = driver.find_element_by_id('Email')
    username_field.send_keys(user)
    next_button = driver.find_element_by_name('signIn')
    next_button.click()
    pw_field = driver.find_element_by_id('Passwd')
    pw_field.send_keys(pswd)
    
    # sign in button is not 'visible' for some reason, just click it with vanilla js.
    driver.execute_script("document.getElementById('signIn').click()")


def main():
    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': "mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(['https://www.youtube.com/watch?v=dQw4w9WgXcQ'])


if __name__ == "__main__":
    #main()
    make_video_list()
