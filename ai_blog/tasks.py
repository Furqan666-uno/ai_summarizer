from celery import shared_task
from django.conf import settings
from .models import BlogPost
from .utils import clean_youtube_link, yt_title, download_audio, sanitize_filename
import assemblyai as aai
from groq import Groq
import re
import os 
    

@shared_task(bind=True)
def generate_blog_task(self, yt_link, user_id):
    try:
        yt_link = clean_youtube_link(yt_link)

        # Get title
        title = yt_title(yt_link)
        if not title:
            return {'error': 'Could not fetch YouTube title'}

        safe_title = sanitize_filename(title)


        audio_file = download_audio(yt_link, safe_title)
        if not audio_file or not os.path.exists(audio_file):
            return {'error': 'Audio download failed'}


        aai.settings.api_key = settings.AAI_API_KEY
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)

        if not transcript.text:
            return {'error': 'Failed to transcribe audio'}

        # ✅ Generate blog using Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        prompt = f"Based on the following transcript, write a professional blog article:\n{transcript.text}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert blog writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )

        blog_content = response.choices[0].message.content.strip()

        BlogPost.objects.create(
            user_id=user_id,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
            audio_file=audio_file
        )

        return {'title': title, 'content': blog_content, 'audio_file': audio_file}

    except Exception as e:
        return {'error': str(e)}

