import yt_dlp
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

# Folder where credentials json file located
os.chdir('C://Users//YOUR_NAME_HERE//YOUR_FOLDER_HERE')

def progress_hook(d):
    title = d.get('info_dict', {}).get('title')
    if d['status'] == 'finished':
        print(f"Downloaded {title}, now converting...")

# Google Sheets auth
credentials_name = "YOUR_CREDENTIAL_FILE_HERE.json"

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_name, scope)
client = gspread.authorize(creds)

# Manually share the sheet with the service account email you've created

# Now check if it sees the sheet
files = client.list_spreadsheet_files()
for f in files:
    print(f['name'], f['id'])

# Open the sheet
sheet = client.open("YOUR_SHEET_NAME_HERE").sheet1

# Get all URLs (skips header in row 1)
urls = sheet.col_values(1)[1:]

# Manually download ffmpeg from https://ffmpeg.org/download.html
# Extract the ZIP. Add the bin folder to your PATH in Env Variables
# Check if it's detected in a new terminal via <ffmpeg -version>

# Specify yt-dlp options 
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,   # True: only single URL downloaded at a time
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': r"C:\YOUR_PATH_TO_FFMPEG_HERE\bin",
    'quiet': True, # True: removes progress updates
    'progress_hooks': [progress_hook] # if you want a minimal progress update
}

# Process each URL and give the output a custom title
for i, url in enumerate(urls, start=2):
    custom_title = sheet.cell(i, 2).value  # column B
    ydl_opts['outtmpl'] = rf"C:\YOUR_DESTINATION_FOLDER_HERE\{custom_title}.%(ext)s"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        sheet.update_cell(i, 3, "Success") # column C
    except Exception as e:
        sheet.update_cell(i, 3, f"Error: {str(e)[:50]}")
