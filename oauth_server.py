"""
Simple OAuth2 callback server for Google authentication
"""
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler for OAuth2 callback"""
    
    def do_GET(self):
        """Handle GET request with authorization code"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/' or parsed_url.path.startswith('/oauth'):
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                # Store the authorization code
                self.server.auth_code = query_params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authorization Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
                        .success { color: #28a745; }
                        .container { max-width: 600px; margin: 0 auto; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="success">✅ Authorization Successful!</h1>
                        <p>Your Telegram bot has been successfully authorized to access your Blogger account.</p>
                        <p><strong>You can now close this tab and return to Telegram.</strong></p>
                        <p>Try creating a post with the <code>/post</code> command in your bot.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
                
            elif 'error' in query_params:
                # Handle authorization error
                error = query_params['error'][0]
                self.server.auth_error = error
                
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authorization Failed</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 50px; text-align: center; }}
                        .error {{ color: #dc3545; }}
                        .container {{ max-width: 600px; margin: 0 auto; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">❌ Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p>Please try again or contact support if the issue persists.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default log messages"""
        pass

class OAuthServer:
    """OAuth2 callback server manager"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.auth_code = None
        self.auth_error = None
    
    def start(self):
        """Start the OAuth callback server"""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), OAuthCallbackHandler)
            self.server.auth_code = None
            self.server.auth_error = None
            
            # Start server in a separate thread
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info(f"OAuth callback server started on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start OAuth server: {e}")
            return False
    
    def stop(self):
        """Stop the OAuth callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            
        if self.thread:
            self.thread.join(timeout=2)
        
        logger.info("OAuth callback server stopped")
    
    def wait_for_callback(self, timeout=300):
        """Wait for OAuth callback with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.server and hasattr(self.server, 'auth_code') and self.server.auth_code:
                self.auth_code = self.server.auth_code
                return self.auth_code
            
            if self.server and hasattr(self.server, 'auth_error') and self.server.auth_error:
                self.auth_error = self.server.auth_error
                return None
            
            time.sleep(1)
        
        return None
    
    def get_redirect_uri(self):
        """Get the redirect URI for this server"""
        return f"http://localhost:{self.port}"