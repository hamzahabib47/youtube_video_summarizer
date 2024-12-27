from flask import Flask, render_template, request
from markdown import markdown
from youtube_transcript_api import YouTubeTranscriptApi
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Configure Generative AI
api_key = os.getenv('api_key')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_yt_link(yt_link):
    # Combine the base path with the query string
    full_url = f"{request.scheme}://{request.host}/link/{yt_link}"
    if request.query_string:
        full_url += f"?{request.query_string.decode('utf-8')}"
    return full_url

def extract_video_id(link):
    """Extracts the video ID from a YouTube link."""
    match = re.search(r"(?:v=|/videos/|embed/|youtu.be/|/v/|/e/)([\w-]{11})", link)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube link. Please provide a valid YouTube video URL.")

def get_video_transcript(video_id):
    """Retrieves the transcript of a YouTube video using the video ID."""
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "hi", "ur", "tr", "es"))
        subtitles = [entry['text'] for entry in srt]
        return ' '.join(subtitles)
    except Exception as e:
        raise RuntimeError(f"Error retrieving transcript: {e}")

@app.route('/')
def home():
    return render_template('prompt.html')

@app.route('/<path:yt_link>')
def generate_from_link(yt_link):
    try:
        full_url = extract_yt_link(yt_link)

        # Extract video ID and get transcript
        video_id = extract_video_id(full_url)
        transcript = get_video_transcript(video_id)

        # Default prompt
        default_prompt = """Please summarize the following YouTube Video by extracting all key points and meaningful insights. Highlight the most important information, significant ideas, and any conclusions or action items. Provide a concise and organized summary, ensuring that all critical details are captured."""

        full_prompt = f"""{default_prompt}\n{transcript}"""
        response = model.generate_content(full_prompt)

        # Convert the response to Markdown format
        formatted_response = markdown(response.text)

        return render_template('main.html', summary=formatted_response)
    except Exception as e:
        return render_template('main.html', error=e)

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get user inputs
        youtube_link = request.form.get('youtube_link')
        user_prompt = request.form.get('user_prompt')

        # Extract video ID and get transcript
        video_id = extract_video_id(youtube_link)
        transcript = get_video_transcript(video_id)

        # Generate AI response using user prompt
        full_prompt = f"""{user_prompt}\n{transcript}"""
        response = model.generate_content(full_prompt)

        # Convert the response to Markdown format
        formatted_response = markdown(response.text)

        return formatted_response
    except Exception as e:
        return markdown(f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=False)
