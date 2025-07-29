"""
Template Processor
Processes the HTML template and replaces placeholders with user data
"""

import logging
import re

logger = logging.getLogger(__name__)

class TemplateProcessor:
    def __init__(self):
        self.template_file = 'permanent_post_template.html'

    def process_template(self, data):
        """Process the HTML template with user data"""
        try:
            # Load the template
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template = f.read()

            # Replace placeholders
            processed_html = template

            # Replace basic placeholders
            processed_html = processed_html.replace('(1#Poster)', data.get('poster', 'DefaultPoster'))
            processed_html = processed_html.replace('(2#Rating)', str(data.get('rating', '0.0')))
            processed_html = processed_html.replace('(3#MovieReview)', data.get('review', 'No review available'))
            processed_html = processed_html.replace('(5#YoutubeEmbedLink)', self._process_youtube_link(data.get('youtube', '')))
            processed_html = processed_html.replace('(6#Year/Month/MovieCode)', data.get('source_data', '2025/01/default'))

            # Process scenes (4#Scene1, 4#Scene2, etc.)
            scenes = self._process_scenes(data.get('scenes', '1,2,3,4'))
            for i, scene in enumerate(scenes, 1):
                processed_html = processed_html.replace(f'(4#Scene{i})', scene)

            return processed_html

        except Exception as e:
            logger.error(f"Error processing template: {e}")
            return f"<p>Error processing template: {str(e)}</p>"

    def _process_youtube_link(self, youtube_url):
        """Convert YouTube URL to embed format"""
        if not youtube_url:
            return "https://www.youtube.com/embed/dQw4w9WgXcQ"  # Default video

        # Extract video ID from various YouTube URL formats
        video_id = None

        # Standard YouTube URL
        if "youtube.com/watch?v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        # Shortened YouTube URL
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        # Already an embed URL
        elif "youtube.com/embed/" in youtube_url:
            return youtube_url

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        else:
            logger.warning(f"Could not extract video ID from: {youtube_url}")
            return youtube_url

    def _process_scenes(self, scenes_input):
        """Process comma-separated scene numbers"""
        try:
            scenes = [s.strip() for s in scenes_input.split(',')]
            # Ensure we have exactly 4 scenes
            while len(scenes) < 4:
                scenes.append('1')  # Default scene number
            return scenes[:4]  # Take only first 4
        except:
            return ['1', '2', '3', '4']  # Default scenes

    def validate_template(self):
        """Validate that the template file exists and contains required placeholders"""
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            required_placeholders = [
                '(1#Poster)', '(2#Rating)', '(3#MovieReview)',
                '(4#Scene1)', '(4#Scene2)', '(4#Scene3)', '(4#Scene4)',
                '(5#YoutubeEmbedLink)', '(6#Year/Month/MovieCode)'
            ]

            missing = []
            for placeholder in required_placeholders:
                if placeholder not in content:
                    missing.append(placeholder)

            if missing:
                logger.warning(f"Missing placeholders in template: {missing}")
                return False, missing

            return True, []

        except FileNotFoundError:
            logger.error(f"Template file not found: {self.template_file}")
            return False, ["Template file not found"]
        except Exception as e:
            logger.error(f"Error validating template: {e}")
            return False, [str(e)]
