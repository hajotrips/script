import os
import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterVideo
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Telegram API credentials
api_id = '21989504'
api_hash = '4581732c2d9c0ce9fea09d61ee9d17a5'
phone = '+918688161647'
chat_username = '+917330868106'

# Google Drive API credentials
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'
FOLDER_NAME = '1zLO9_1JqmCho-gKvbvoP1dajlPHjDykH'


DOWNLOADS_DIR = os.path.expanduser('~/Downloads')

# Initialize Telegram client
client = TelegramClient('hajo', api_id, api_hash)

# Initialize Google Drive client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)


async def download_media():
    await client.start(phone)
    async for message in client.iter_messages(chat_username, filter=InputMessagesFilterPhotos()):
        if message.media:
            print("Downloading photo...")
            file_path = await client.download_media(message, file=DOWNLOADS_DIR)
            if file_path:
                print(f"Downloaded photo to {file_path}")
                #deliver_to_google_drive(file_path, credentials, FOLDER_NAME)
            else:
                print("Failed to download photo")

    async for message in client.iter_messages(chat_username, filter=InputMessagesFilterVideo()):
        if message.media:
            print("Downloading video...")
            file_path = await client.download_media(message, file=DOWNLOADS_DIR)
            if file_path:
                print(f"Downloaded video to {file_path}")
                #deliver_to_google_drive(file_path, credentials, FOLDER_NAME)
            else:
                print("Failed to download video")

def deliver_to_google_drive(output_file, creds, folder_to_store_files):
    print("uploading...")
    drive_service = build('drive', 'v3', credentials=creds)
    page_token = None
    while True:
        query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_to_store_files}'"
        response = drive_service.files().list(q=query,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              includeItemsFromAllDrives=True,
                                              supportsAllDrives=True,
                                              pageToken=page_token).execute()

        print("response from listing: ",response)
        
        for folder in response.get('files', []):
            print(f'Found folder: {folder.get("name")} ({folder.get("id")})')
            filename = os.path.basename(output_file)
            print(filename)
            file_metadata = {
                'parents': [folder.get('id')],
                'name': filename
            }
            media = MediaFileUpload(output_file, resumable=True)
            file = drive_service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id',
                                                supportsAllDrives=True).execute()
            print(f'File ID: {file.get("id")}')
            os.remove(output_file)

        print("UPLOADED")
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break



if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(download_media())
