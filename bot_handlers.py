"""
Telegram Bot Handlers
Handles all bot commands and user interactions
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from blogger_client import BloggerClient
from template_processor import TemplateProcessor
from simple_oauth import SimpleBloggerAuth

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.blogger_client = BloggerClient()
        self.template_processor = TemplateProcessor()
        
        # User states for conversation tracking
        self.user_states = {}
        
        # Data collection steps
        self.STEPS = [
            'title', 'labels', 'poster', 'rating', 'review', 
            'scenes', 'youtube', 'source_data'
        ]
        
        self.STEP_PROMPTS = {
            'title': 'Please enter the movie title:',
            'labels': 'Please enter labels (comma-separated):',
            'poster': 'Please enter the poster image name (e.g., MovieName):',
            'rating': 'Please enter the movie rating (e.g., 8.5):',
            'review': 'Please enter your movie review:',
            'scenes': 'Please enter scene numbers (comma-separated, e.g., 1,2,3,4):',
            'youtube': 'Please enter the YouTube embed link:',
            'source_data': 'Please enter source data (Year/Month/MovieCode, e.g., 2025/08/asd5tg):'
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = (
            "🎬 Welcome to the Blogger Movie Post Bot!\n\n"
            "I can help you create and publish movie review posts to your Blogger blog.\n\n"
            "Available commands:\n"
            "/post - Start creating a new movie post\n"
            "/cancel - Cancel current operation\n"
            "/edit - Edit current post data\n"
            "/help - Show this help message\n\n"
            "Use /post to get started!"
        )
        await update.message.reply_text(welcome_msg)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = (
            "🎬 Blogger Movie Post Bot Help\n\n"
            "Available Commands:\n"
            "/start - Welcome message and introduction\n"
            "/post - Start creating a new movie post\n"
            "/cancel - Cancel current posting process\n"
            "/edit - Edit any field in your current post\n"
            "/status - Check your current post status\n"
            "/template - View the HTML template structure\n"
            "/auth - Check Google Blogger authentication status\n"
            "/complete_auth - Complete Google authentication after authorization\n"
            "/help - Show this help message\n\n"
            "How to use:\n"
            "1. Use /post to start creating a post\n"
            "2. Follow the step-by-step prompts:\n"
            "   • Title - Movie title\n"
            "   • Labels - Tags (comma-separated)\n" 
            "   • Poster - Image name for poster\n"
            "   • Rating - Movie rating (0-10)\n"
            "   • Review - Your movie review text\n"
            "   • Scenes - Scene numbers (1,2,3,4)\n"
            "   • YouTube - Video embed link\n"
            "   • Source - Year/Month/Code format\n"
            "3. Review and edit if needed\n"
            "4. Confirm to publish to your blog\n\n"
            "Tips:\n"
            "• You can use /cancel anytime to stop\n"
            "• Use /edit to modify any field during creation\n"
            "• All fields are validated before posting"
        )
        await update.message.reply_text(help_msg)
    
    async def post_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post command - start the posting process"""
        user_id = update.effective_user.id
        
        # Initialize user state
        self.user_states[user_id] = {
            'step': 0,
            'data': {},
            'in_edit_mode': False
        }
        
        # Start with first step
        await self._ask_next_question(update, context, user_id)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        user_id = update.effective_user.id
        
        if user_id in self.user_states:
            del self.user_states[user_id]
            await update.message.reply_text("❌ Post creation cancelled.")
        else:
            await update.message.reply_text("No active post creation to cancel.")
    
    async def edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /edit command"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states:
            await update.message.reply_text("No active post to edit. Use /post to start creating a post.")
            return
        
        # Show edit options
        await self._show_edit_options(update, context, user_id)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command - show current post status"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states:
            await update.message.reply_text("📝 No active post creation in progress.\nUse /post to start creating a new movie post.")
            return
        
        user_state = self.user_states[user_id]
        current_step = user_state['step']
        data = user_state['data']
        
        status_msg = "📊 **Current Post Status:**\n\n"
        
        for i, step in enumerate(self.STEPS):
            step_display = step.replace('_', ' ').title()
            if i < current_step:
                value = data.get(step, 'Not set')
                if step == 'review' and len(value) > 50:
                    value = value[:50] + '...'
                status_msg += f"✅ {step_display}: {value}\n"
            elif i == current_step:
                status_msg += f"➡️ {step_display}: *Currently asking*\n"
            else:
                status_msg += f"⏳ {step_display}: *Pending*\n"
        
        status_msg += f"\nProgress: {current_step}/{len(self.STEPS)} steps completed"
        
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def template_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /template command - show template structure"""
        template_info = (
            "🏗️ **HTML Template Structure:**\n\n"
            "The bot uses the following placeholders in the HTML template:\n\n"
            "**Replacements:**\n"
            "• `(1#Poster)` → Poster image name\n"
            "• `(2#Rating)` → Movie rating\n"
            "• `(3#MovieReview)` → Your review text\n"
            "• `(4#Scene1-4)` → Scene image numbers\n"
            "• `(5#YoutubeEmbedLink)` → YouTube embed URL\n"
            "• `(6#Year/Month/MovieCode)` → Source data\n\n"
            "**Features:**\n"
            "• Auto-scrolling image gallery\n"
            "• Responsive YouTube embed\n"
            "• Rating badge overlay\n"
            "• Random posts section\n"
            "• Mobile-optimized styling\n\n"
            "All placeholders are validated and processed automatically when you create a post."
        )
        
        await update.message.reply_text(template_info, parse_mode='Markdown')
    
    async def auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /auth command - show authentication status and help"""
        try:
            # Check current authentication status
            auth_status = self.blogger_client.authenticate()
            
            if auth_status == True:
                await update.message.reply_text(
                    "✅ **Authentication Status: ACTIVE**\n\n"
                    "Your bot is successfully connected to Google Blogger API.\n"
                    "You can create and publish posts without any issues."
                )
            elif auth_status == "auth_required":
                auth_url = getattr(self.blogger_client, 'auth_url', None)
                if auth_url:
                    await update.message.reply_text(
                        f"🔐 **Authentication Required**\n\n"
                        f"To publish posts to Blogger, you need to authorize this application.\n\n"
                        f"**Steps to complete setup:**\n"
                        f"1. Click this URL: {auth_url}\n\n"
                        f"2. Sign in with your Google account\n"
                        f"3. Grant permission to access Blogger\n"
                        f"4. You'll be redirected to a success page\n"
                        f"5. Return here and use /complete_auth to finish setup\n\n"
                        f"**Note:** This is a one-time setup process."
                    )
                else:
                    await update.message.reply_text(
                        "❌ Authentication setup required. Please contact administrator."
                    )
            else:
                await update.message.reply_text(
                    f"❌ Authentication failed: {auth_status}"
                )
                
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error checking authentication: {str(e)}"
            )
    
    async def complete_auth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /complete_auth command - complete OAuth authentication"""
        try:
            await update.message.reply_text("🔄 Checking authentication status...")
            
            # Use simple authentication check instead of complex OAuth flow
            simple_auth = SimpleBloggerAuth()
            auth_result = simple_auth.authenticate()
            
            if auth_result == True:
                await update.message.reply_text(
                    "✅ **Authentication Successful!**\n\n"
                    "Your bot is now connected to Google Blogger API.\n"
                    "You can now create and publish posts using /post command."
                )
            else:
                instructions = simple_auth.get_auth_instructions()
                await update.message.reply_text(instructions)
                
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error checking authentication: {str(e)}"
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages during conversation"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states:
            await update.message.reply_text(
                "Please use /post to start creating a new movie post."
            )
            return
        
        user_state = self.user_states[user_id]
        user_input = update.message.text.strip()
        
        # Check if user is in edit mode
        if user_state.get('in_edit_mode', False):
            field = user_state.get('editing_field')
            if field and await self._validate_input(field, user_input, update):
                user_state['data'][field] = user_input
                user_state['in_edit_mode'] = False
                user_state.pop('editing_field', None)
                
                await update.message.reply_text(f"✅ {field.replace('_', ' ').title()} updated successfully!")
                await self._show_final_confirmation(update, context, user_id)
            return
        
        current_step = user_state['step']
        
        if current_step < len(self.STEPS):
            step_name = self.STEPS[current_step]
            
            # Validate and store input
            if await self._validate_input(step_name, user_input, update):
                user_state['data'][step_name] = user_input
                user_state['step'] += 1
                
                # Check if we've collected all data
                if user_state['step'] >= len(self.STEPS):
                    await self._show_final_confirmation(update, context, user_id)
                else:
                    await self._ask_next_question(update, context, user_id)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if user_id not in self.user_states:
            await query.edit_message_text("Session expired. Please use /post to start again.")
            return
        
        if data == "post_confirm":
            await self._publish_post(query, context, user_id)
        elif data == "post_cancel":
            del self.user_states[user_id]
            await query.edit_message_text("❌ Post creation cancelled.")
        elif data == "post_edit":
            await self._show_edit_options_callback(query, context, user_id)
        elif data.startswith("edit_"):
            field = data.replace("edit_", "")
            await self._start_field_edit(query, context, user_id, field)
    
    async def _ask_next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Ask the next question in the sequence"""
        user_state = self.user_states[user_id]
        current_step = user_state['step']
        
        if current_step < len(self.STEPS):
            step_name = self.STEPS[current_step]
            prompt = self.STEP_PROMPTS[step_name]
            
            step_number = current_step + 1
            total_steps = len(self.STEPS)
            
            message = f"📝 Step {step_number}/{total_steps}: {prompt}"
            await update.message.reply_text(message)
    
    async def _validate_input(self, step_name: str, user_input: str, update: Update) -> bool:
        """Validate user input based on the step"""
        if not user_input:
            await update.message.reply_text("❌ Input cannot be empty. Please try again.")
            return False
        
        if step_name == "rating":
            try:
                rating = float(user_input)
                if rating < 0 or rating > 10:
                    await update.message.reply_text("❌ Rating should be between 0 and 10. Please try again.")
                    return False
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number for rating.")
                return False
        
        elif step_name == "scenes":
            scenes = [s.strip() for s in user_input.split(',')]
            if len(scenes) != 4:
                await update.message.reply_text("❌ Please provide exactly 4 scene numbers separated by commas (e.g., 1,2,3,4).")
                return False
        
        elif step_name == "youtube":
            if "youtube.com" not in user_input and "youtu.be" not in user_input:
                await update.message.reply_text("❌ Please provide a valid YouTube link.")
                return False
        
        elif step_name == "source_data":
            parts = user_input.split('/')
            if len(parts) != 3:
                await update.message.reply_text("❌ Please use the format: Year/Month/MovieCode (e.g., 2025/08/asd5tg)")
                return False
        
        return True
    
    async def _show_final_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show final confirmation with collected data"""
        user_state = self.user_states[user_id]
        data = user_state['data']
        
        # Create summary
        summary = "📋 **Post Summary:**\n\n"
        summary += f"🎬 **Title:** {data.get('title', 'N/A')}\n"
        summary += f"🏷️ **Labels:** {data.get('labels', 'N/A')}\n"
        summary += f"🖼️ **Poster:** {data.get('poster', 'N/A')}\n"
        summary += f"⭐ **Rating:** {data.get('rating', 'N/A')}\n"
        summary += f"📝 **Review:** {data.get('review', 'N/A')[:100]}{'...' if len(data.get('review', '')) > 100 else ''}\n"
        summary += f"🎞️ **Scenes:** {data.get('scenes', 'N/A')}\n"
        summary += f"📺 **YouTube:** {data.get('youtube', 'N/A')}\n"
        summary += f"📂 **Source:** {data.get('source_data', 'N/A')}\n\n"
        summary += "What would you like to do?"
        
        # Create buttons
        keyboard = [
            [InlineKeyboardButton("✏️ Edit", callback_data="post_edit")],
            [InlineKeyboardButton("❌ Cancel", callback_data="post_cancel")],
            [InlineKeyboardButton("✅ POST", callback_data="post_confirm")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_edit_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show edit options"""
        keyboard = []
        for step in self.STEPS:
            button_text = step.replace('_', ' ').title()
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"edit_{step}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Which field would you like to edit?", reply_markup=reply_markup)
    
    async def _show_edit_options_callback(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show edit options via callback"""
        keyboard = []
        for step in self.STEPS:
            button_text = step.replace('_', ' ').title()
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"edit_{step}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Which field would you like to edit?", reply_markup=reply_markup)
    
    async def _start_field_edit(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int, field: str):
        """Start editing a specific field"""
        user_state = self.user_states[user_id]
        user_state['editing_field'] = field
        user_state['in_edit_mode'] = True
        
        prompt = self.STEP_PROMPTS.get(field, f"Enter new value for {field}:")
        current_value = user_state['data'].get(field, 'Not set')
        
        message = f"Current value: {current_value}\n\n{prompt}"
        await query.edit_message_text(message)
    
    async def _publish_post(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Publish the post to Blogger"""
        await query.edit_message_text("📤 Publishing post to Blogger...")
        
        try:
            user_state = self.user_states[user_id]
            data = user_state['data']
            
            # Process the HTML template
            html_content = self.template_processor.process_template(data)
            
            # Create the post
            success, result = self.blogger_client.create_post(
                title=data['title'],
                content=html_content,
                labels=data.get('labels')
            )
            
            if success:
                await query.edit_message_text(
                    f"✅ Post published successfully!\n\n🔗 URL: {result}"
                )
            elif result == "Authentication failed":
                # Check if we have an auth URL available
                auth_url = getattr(self.blogger_client, 'auth_url', None)
                if auth_url:
                    await query.edit_message_text(
                        f"🔐 **Authentication Required**\n\n"
                        f"To publish posts to Blogger, you need to authorize this application.\n\n"
                        f"**Please follow these steps:**\n"
                        f"1. Click this URL: {auth_url}\n\n"
                        f"2. Sign in with your Google account\n"
                        f"3. Grant permission to access Blogger\n"
                        f"4. You'll be redirected to a success page\n"
                        f"5. Return here and use /complete_auth to finish setup\n\n"
                        f"**Note:** This is a one-time setup process."
                    )
                else:
                    await query.edit_message_text(
                        f"❌ Authentication failed. Please use /auth command to set up Google Blogger access."
                    )
            else:
                await query.edit_message_text(
                    f"❌ Failed to publish post:\n{result}"
                )
            
            # Clean up user state
            del self.user_states[user_id]
            
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            await query.edit_message_text(
                f"❌ An error occurred while publishing:\n{str(e)}"
            )
