# drive-tunes

A wrapper around [youtube-dl](https://github.com/rg3/youtube-dl) to scrape mp3s from a spreadsheet in google drive. Follow the first part in the [sheets api quickstart](https://developers.google.com/sheets/api/quickstart/python) to get a working `client_secret.json` (and make sure that's what it's named). 

needs the following:
```bash
pip install --upgrade google-api-python-client
brew install libav
```
libav is for ffmpeg, install might differ a bit on windows or linux.

### todo
Modify to use some cmd line options, currently the save directory and google sheet are hardcoded.
