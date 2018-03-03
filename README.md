# drive-tunes

A wrapper around [youtube-dl](https://github.com/rg3/youtube-dl) to scrape mp3s from a spreadsheet in google drive. Follow the first part in the [sheets api quickstart](https://developers.google.com/sheets/api/quickstart/python) to get a working `client_secret.json` (and make sure that's what it's named). 

update: there's now an easy install option, get your sheet id and client secret and put them in setup.yml then run `ansible-playbook setup.yml -K` to install everything. You will need --ask-vault-pass if you use ansible-vault to encrypt your secrets. This method spits out a tunes.sh that wraps the venv and exports your sheet ID automatically for you.

needs the following:
```bash
sudo apt-get install python3-pip python3-venv libav-tools
git clone https://github.com/glaaki/drive-tunes.git
python3 -m venv drive-tunes/
source drive-tunes/bin/activate
pip install -r drive-tunes/requirements.txt
```
for mac you can `brew install libav` instead of the above libav-tools (ffmpeg is really what we're after)

### todo
* Modify to automatically copy to the proper directory.
* Could use the script to properly set up the labels and sheet tabs.

### example sheet
The script skips row 1 so set up your sheet like this:

| Artist      | Title  | Album  | Link |
| ----------- | ------ | ------ | ---- |
| artistname1 | title1 | album1 | https://www.youtube.com/watch?v=dQw4w9WgXcQ |
| artistname2 | title2 | album2 | https://www.youtube.com/watch?v=dQw4w9WgXcQ |

Tab1 should be labeled 'Song Data' and tab2 should be 'Previously Downloaded'.
