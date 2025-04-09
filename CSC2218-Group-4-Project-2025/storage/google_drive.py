"""
Google Drive implementation of the storage strategy.
"""
import os
import json
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request

from storage.strategy import StorageStrategy


class GoogleDriveStorage(StorageStrategy):
    """
    Google Drive implementation of storage strategy.
    """
    # If modifying these scopes, delete the token.json file.
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, token_path='token.json', credentials_path='drive_credentials.json'):
        """
        Initialize with token and credentials paths.
        
        Args:
            token_path (str): Path to the token.json file
            credentials_path (str): Path to the credentials.json file
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Google Drive API.
        
        Returns:
            bool: True if authentication was successful, False otherwise
            str: Error message if authentication failed
        """
        try:
            # Check if token.json exists
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_info(
                    json.loads(open(self.token_path).read()), self.SCOPES)
            
            # If there are no valid credentials available, prompt the user to log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    # If token is expired but we have a refresh token, refresh the token
                    self.creds.refresh(Request())
                else:
                    # If no token exists or it can't be refreshed, get a new one
                    if not os.path.exists(self.credentials_path):
                        return False, "Credentials file not found"
                    
                    # Start OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    
                    # For a desktop app, use run_local_server
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for the next run
                    with open(self.token_path, 'w') as token:
                        token.write(self.creds.to_json())
            
            # Create Drive API client
            self.service = build('drive', 'v3', credentials=self.creds)
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def upload(self, content, metadata):
        """
        Upload content to Google Drive.
        
        Args:
            content (str): The content to upload
            metadata (dict): Metadata for the file
                - category (str): The category of the note
                - title (str): The title of the file (optional)
                
        Returns:
            dict: Result of the upload operation
                - success (bool): Whether the upload was successful
                - message (str): Success or error message
                - link (str, optional): Link to the uploaded file
                - error (str, optional): Detailed error message
        """
        try:
            # Authenticate first
            auth_success, auth_error = self.authenticate()
            if not auth_success:
                return {
                    'success': False, 
                    'message': 'Authentication failed',
                    'error': auth_error
                }
            
            # Generate file name
            category = metadata.get('category', 'Uncategorized')
            title = metadata.get('title')
            
            if not title:
                # Use the first 30 chars of content as title if not provided
                title = content[:30] + ('...' if len(content) > 30 else '')
            
            file_name = f"Note - {category} - {title}"
            
            # Prepare file metadata
            file_metadata = {
                'name': file_name,
                'mimeType': 'text/plain'
            }
            
            # Create an in-memory text file to upload
            file_content = io.BytesIO(content.encode('utf-8'))
            media = MediaIoBaseUpload(file_content, mimetype='text/plain')
            
            # Upload the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Get the file ID
            file_id = file.get('id')
            
            if file_id:
                # Make the file readable by anyone with the link
                self.service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'},
                    fields='id'
                ).execute()
                
                # Get the web view link
                file = self.service.files().get(
                    fileId=file_id,
                    fields='webViewLink'
                ).execute()
                
                web_link = file.get('webViewLink')
                
                return {
                    'success': True,
                    'message': 'File uploaded successfully',
                    'link': web_link,
                    'file_id': file_id
                }
            
            return {
                'success': False,
                'message': 'Failed to upload file',
                'error': 'No file ID returned'
            }
            
        except HttpError as error:
            return {
                'success': False,
                'message': 'HTTP error occurred',
                'error': str(error)
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'An error occurred',
                'error': str(e)
            }