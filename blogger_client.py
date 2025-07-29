"""
Blogger API Client
Handles authentication and posting to Blogger
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from oauth_server import OAuthServer

logger = logging.getLogger(__name__)

class BloggerClient:
    def __init__(self):
        self.blog_id = "4271522061163006364"  # From the provided blog URL
        self.credentials = None
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/blogger']
        
    def authenticate(self):
        """Authenticate with Google OAuth2"""
        try:
            # Load client secrets
            with open('client_secret.json', 'r') as f:
                client_config = json.load(f)
            
            # Check if we have stored credentials
            if os.path.exists('token.json'):
                self.credentials = Credentials.from_authorized_user_file('token.json', self.scopes)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Start OAuth server for callback
                    oauth_server = OAuthServer(port=8080)
                    if not oauth_server.start():
                        logger.error("Failed to start OAuth callback server")
                        return "auth_server_failed"
                    
                    try:
                        # Create flow with proper redirect URI
                        flow = Flow.from_client_config(client_config, self.scopes)
                        flow.redirect_uri = oauth_server.get_redirect_uri()
                        
                        # Generate authorization URL
                        auth_url, _ = flow.authorization_url(
                            prompt='consent',
                            access_type='offline'
                        )
                        
                        logger.info(f"Please visit this URL to authorize the application: {auth_url}")
                        
                        # Store the auth URL and flow for the bot to use
                        self.auth_url = auth_url
                        self.oauth_flow = flow
                        self.oauth_server = oauth_server
                        
                        return "auth_required"
                        
                    except Exception as e:
                        oauth_server.stop()
                        logger.error(f"Failed to create OAuth flow: {e}")
                        return False
            
            # Save the credentials for the next run (only if we have valid credentials)
            if self.credentials and self.credentials.valid:
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())
                
                # Build the service
                self.service = build('blogger', 'v3', credentials=self.credentials)
                return True
            else:
                return "auth_required"
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def complete_oauth_flow(self):
        """Complete the OAuth flow by waiting for callback"""
        try:
            if not hasattr(self, 'oauth_server') or not hasattr(self, 'oauth_flow'):
                return False, "OAuth flow not initialized. Please start with /auth command first."
            
            # Wait for callback (30 seconds timeout to avoid hanging)
            auth_code = self.oauth_server.wait_for_callback(timeout=30)
            
            if auth_code:
                # Exchange authorization code for credentials
                self.oauth_flow.fetch_token(code=auth_code)
                self.credentials = self.oauth_flow.credentials
                
                # Save credentials
                with open('token.json', 'w') as token:
                    token.write(self.credentials.to_json())
                
                # Build the service
                self.service = build('blogger', 'v3', credentials=self.credentials)
                
                self.oauth_server.stop()
                return True, "Authentication successful"
            
            elif hasattr(self.oauth_server, 'auth_error') and self.oauth_server.auth_error:
                self.oauth_server.stop()
                return False, f"OAuth error: {self.oauth_server.auth_error}"
            
            else:
                self.oauth_server.stop()
                return False, "No authorization received. Please complete the OAuth process in your browser first, then try /complete_auth again."
                
        except Exception as e:
            if hasattr(self, 'oauth_server'):
                self.oauth_server.stop()
            logger.error(f"OAuth completion failed: {e}")
            return False, f"OAuth completion failed: {str(e)}"
    
    def create_post(self, title, content, labels=None):
        """Create a new blog post"""
        try:
            if not self.service:
                auth_result = self.authenticate()
                if auth_result != True:
                    if auth_result == "auth_required":
                        return False, "Authentication failed"
                    else:
                        return False, "Authentication failed"
            
            post_data = {
                'title': title,
                'content': content
            }
            
            if labels:
                # Clean up labels - remove extra spaces and split by comma
                label_list = [label.strip() for label in labels.split(',') if label.strip()]
                post_data['labels'] = label_list
            
            # Create the post
            request = self.service.posts().insert(blogId=self.blog_id, body=post_data)
            response = request.execute()
            
            post_url = response.get('url', 'Unknown URL')
            logger.info(f"Post created successfully: {post_url}")
            
            return True, post_url
            
        except HttpError as e:
            error_msg = f"HTTP Error: {e.resp.status} - {e.content.decode()}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_blog_info(self):
        """Get blog information for testing"""
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            request = self.service.blogs().get(blogId=self.blog_id)
            response = request.execute()
            return response
            
        except Exception as e:
            logger.error(f"Failed to get blog info: {e}")
            return None
