# https://github.com/XtremeRahul/gdrive_folder_size/blob/master/gDrive_calculator.py

import re
import os


import urllib.parse as urlparse
from urllib.parse import parse_qs


from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_readable_file_size(size_in_bytes) -> str:
    SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'


class GoogleDriveSizeCalculate:
    def __init__(self, service=None):
        self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__service = service
        if service is None:
            print("Pass service to GoogleDriveSizeCalculate class. Please fully read the instructions given in the repo.")
            return
        self.total_bytes = 0
        self.total_files = 0
        self.total_folders = 0

    @staticmethod
    def getIdFromUrl(link: str):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex,link)
            if res is None:
                return "GDrive ID not found. Try sending url in different format."
            return res.group(5)
        parsed = urlparse.urlparse(link)
        return parse_qs(parsed.query)['id'][0]

    def gdrive_checker(self, LINKorID):
        if self.__service is None:
            return
        if 'drive.google.com' in LINKorID:
            try:
                file_id = self.getIdFromUrl(LINKorID)
                if 'GDrive ID not found.' in file_id:
                    print(file_id)
                    return
            except (KeyError, IndexError):
                print("GDrive ID could not be found in the provided link.")
                return
        else:
            file_id = LINKorID.strip()

        error = False
        print("Calculating... Please Wait!")

        try:
            drive_file = self.__service.files().get(fileId=file_id, fields="id, name, mimeType, size",
                                                   supportsTeamDrives=True).execute()
            name = drive_file['name']
            if drive_file['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                typee = 'Folder'
                self.total_folders += 1
                self.gDrive_directory(**drive_file)
            else:
                try:
                    typee = drive_file['mimeType']
                except:
                    typee = 'File'
                self.total_files += 1
                self.gDrive_file(**drive_file)
            print("Calculated")
            

        except Exception as e:
            print('\n')
            if 'HttpError' in str(e):
                h_e = str(e)
                ori = h_e
                try:
                    h_e = h_e.replace('<', '').replace('>', '')
                    h_e = h_e.split('when')
                    f = h_e[0].strip()
                    s = h_e[1].split('"')[1].split('"')[0].strip()
                    e =  f"{f}\n{s}"
                except:
                    e = ori
            print(str(e))
            error = True
        finally:
            if error:
                return
            return {
                'name': name,
                'size': get_readable_file_size(self.total_bytes),
                'bytes': self.total_bytes,
                'type': typee,
                'files': self.total_files,
                'folders': self.total_folders
                }

    def list_drive_dir(self, file_id: str) -> list:
        query = f"'{file_id}' in parents and (name contains '*')"
        fields = 'nextPageToken, files(id, mimeType, size)'
        page_token = None
        page_size = 1000
        files = []
        while True:
            response = self.__service.files().list(supportsTeamDrives=True,
                                                  includeTeamDriveItems=True,
                                                  q=query, spaces='drive',
                                                  fields=fields, pageToken=page_token,
                                                  pageSize=page_size, corpora='allDrives',
                                                  orderBy='folder, name').execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files

    def gDrive_file(self, **kwargs):
        try:
            size = int(kwargs['size'])
        except:
            size = 0
        self.total_bytes += size

    def gDrive_directory(self, **kwargs) -> None:
        files = self.list_drive_dir(kwargs['id'])
        if len(files) == 0:
            return
        for file_ in files:
            if file_['mimeType'] == self.__G_DRIVE_DIR_MIME_TYPE:
                self.total_folders += 1
                self.gDrive_directory(**file_)
            else:
                self.total_files += 1
                self.gDrive_file(**file_)


credentials = None
oauth_scope = ['https://www.googleapis.com/auth/drive']


client_email = os.getenv("sa_email")
private_key = os.getenv("private_key")
if private_key:
    private_key = private_key.replace("\\n",'\n')

sa = dict()
sa["client_email"] = client_email
sa["token_uri"] = 'https://oauth2.googleapis.com/token'
sa["private_key"] = private_key

if client_email and private_key:
    credentials = service_account.Credentials.from_service_account_info(sa,scopes=oauth_scope)
    service =  build('drive', 'v3', credentials=credentials, cache_discovery=False)
else:
    credentials = None
    service = None

