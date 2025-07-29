"""
Simple OAuth2 implementation that doesn't require a callback server
Uses device flow or simplified authentication
"""
import json
import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class SimpleBloggerAuth:
    """Simplified Blogger authentication without callback server"""
    
    def __init__(self):
        self.blog_id = "4271522061163006364"
        self.credentials = None
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/blogger']
    
    def authenticate(self):
        """Authenticate using simple method"""
        try:
            # Check if we have stored credentials
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                    except Exception as e:
                        logger.error(f"Token refresh failed: {e}")
                        return "auth_required"
                else:
                    return "auth_required"
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.credentials.to_json())
            
            # Build the service
            self.service = build('blogger', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_auth_instructions(self):
        """Get manual authentication instructions"""
        return """
🔐 **Manual Authentication Required**

Since the automatic OAuth flow has issues, please set up authentication manually:

**Option 1: Use Google Cloud Console**
1. Go to https://console.cloud.google.com
2. Create a new project or select existing
3. Enable Blogger API
4. Create OAuth2 credentials (Desktop application)
5. Download the credentials as client_secret.json

**Option 2: Contact for Setup**
The authentication requires manual setup. Please contact support for assistance with:
- Google Cloud Console configuration
- OAuth2 credential setup
- Token generation

**Current Status:** Bot is working but needs valid Google credentials to publish posts.
        """
    
    def create_post(self, title, content, labels=None):
        """Create a new blog post"""
        try:
            if not self.service:
                auth_result = self.authenticate()
                if auth_result != True:
                    return False, "Authentication required - please set up Google OAuth2 credentials"
            
            post_data = {
                'title': title,
                'content': content
            }
            
            if labels:
                label_list = [label.strip() for label in labels.split(',') if label.strip()]
                post_data['labels'] = label_list
            
            # Create the post
            request = self.service.posts().insert(blogId=self.blog_id, body=post_data)
            response = request.execute()
            
            post_url = response.get('url', 'Unknown URL')
            logger.info(f"Post created successfully: {post_url}")
            return True, post_url
            
        except Exception as e:
            logger.error(f"Post creation failed: {e}")
            return False, f"Post creation failed: {str(e)}"