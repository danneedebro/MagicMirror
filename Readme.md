# Magic Mirror

## Main Installation
1. Clone this repository
2. Create a virtual enviroment `>>python -m venv <venv-folder-name>`
3. Activate virtual enviroment    
 `venv\Scripts\activate.bat`    (Windows)    
 `source venv/bin/activate`    (Linux)

4. Install packages `>>python -m pip install -r requirements.txt`
(Note: there might be problem installing wx on raspberry)

## Installation/preparation of modules
Different modules talks to different web services and might need installing

### Google Calendar set up
1. Create a Google API credentials file named `credentials.json` in step 1 in this link: [Python Quickstart](https://developers.google.com/calendar/quickstart/python) or in the [Google APIs console](https://console.developers.google.com) (APIs & Services...Credentials).
2. Run the file `GoogleCalendar/GoogleCalendar.py` directly
[Hej](sdsd)