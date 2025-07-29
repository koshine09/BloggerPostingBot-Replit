# Telegram Blogger Bot

## Overview

This is a Telegram bot that automates posting movie reviews to a Blogger blog. The bot collects movie information from users through a conversational interface, processes an HTML template with the provided data, and publishes the formatted post to a specific Blogger blog using Google's Blogger API.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

- **Main Application Layer**: Entry point and bot configuration (`main.py`)
- **Bot Handler Layer**: Telegram bot interaction and conversation management (`bot_handlers.py`)
- **Template Processing Layer**: HTML template processing and data substitution (`template_processor.py`)
- **External API Layer**: Google Blogger API integration (`blogger_client.py`)
- **Static Assets**: HTML template and configuration files

## Key Components

### Telegram Bot Interface
- Built using `python-telegram-bot` library
- Implements conversational flow for data collection
- Supports commands: `/start`, `/post`, `/cancel`, `/edit`, `/help`
- Uses inline keyboards for user interaction
- Maintains user state throughout conversation

### Data Collection System
The bot collects the following movie data through a multi-step conversation:
- Movie title
- Labels (comma-separated tags)
- Poster image name
- Movie rating
- Movie review text
- Scene numbers for image gallery
- YouTube embed link
- Source data (Year/Month/MovieCode format)

### Template Processing Engine
- Processes HTML template with placeholder substitution
- Handles dynamic content replacement using pattern matching
- Supports multiple scene images in scrollable gallery
- Processes YouTube links for proper embedding
- Maintains original HTML structure and styling

### Blogger API Integration
- Uses Google OAuth2 for authentication
- Implements credential management with token persistence
- Handles blog post creation and publishing
- Error handling for API failures
- Targets specific blog ID: `4271522061163006364`

## Data Flow

1. **User Interaction**: User starts conversation with `/post` command
2. **Data Collection**: Bot guides user through step-by-step data entry
3. **Template Processing**: Collected data is merged with HTML template
4. **Authentication**: Google OAuth2 flow for Blogger API access
5. **Publishing**: Formatted post is published to Blogger blog
6. **Confirmation**: User receives success/failure notification

## External Dependencies

### Python Libraries
- `python-telegram-bot`: Telegram Bot API wrapper
- `google-auth-oauthlib`: Google OAuth2 authentication
- `google-auth`: Google authentication utilities  
- `google-api-python-client`: Google APIs client library

### External Services
- **Telegram Bot API**: Bot communication platform
- **Google Blogger API**: Blog post publishing
- **Google OAuth2**: Authentication and authorization
- **Archive.org**: Image hosting for movie posters and scenes

### Configuration Files
- `client_secret.json`: Google OAuth2 client credentials
- `token.json`: Stored OAuth2 access tokens (generated at runtime)
- `permanent_post_template.html`: HTML template for blog posts

## Deployment Strategy

### Environment Setup
- Bot token stored as environment variable (`TELEGRAM_BOT_TOKEN`)
- OAuth2 credentials in `client_secret.json`
- Python environment with required dependencies

### Authentication Flow
- Initial OAuth2 setup requires manual authorization
- Subsequent runs use stored refresh tokens
- Fallback to re-authorization if tokens expire

### Error Handling
- Comprehensive logging throughout application
- Graceful handling of API failures
- User-friendly error messages
- Conversation state recovery options

The application is designed for single-user operation with a specific Blogger blog, making it suitable for personal movie review automation.

## Recent Changes

### July 29, 2025 - Complete Bot Implementation
- ✓ Successfully created and deployed Telegram bot for automated Blogger posting
- ✓ Implemented all core functionality as requested:
  - Step-by-step data collection (Title, Labels, Poster, Rating, Review, Scenes, YouTube, Source)
  - HTML template processing with placeholder replacement system
  - Google Blogger API integration with OAuth2 authentication
  - Interactive conversation flow with validation
  - Edit functionality for modifying collected data
  - Cancel command for aborting current operations
- ✓ Added helpful additional commands:
  - /status - Shows current post creation progress
  - /template - Displays HTML template structure information
  - Enhanced /help with detailed usage instructions
- ✓ Applied user's permanent HTML template with all required placeholders
- ✓ Updated client credentials for Google API access
- ✓ Bot is successfully running and ready for production use

### Bot Status: ACTIVE
- Bot Token: Configured and functional
- Blog ID: 4271522061163006364 (configured)  
- All commands operational and tested
- Ready for user interaction via Telegram
