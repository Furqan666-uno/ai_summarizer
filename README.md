<img width="1919" height="838" alt="Screenshot 2025-08-18 215631" src="https://github.com/user-attachments/assets/b9e50b72-a08c-4a61-9338-e49ab6e6a4aa" />

<img width="1919" height="879" alt="image" src="https://github.com/user-attachments/assets/9e80f27a-2441-4e2a-8ced-07a650534d96" />

<img width="1919" height="878" alt="image" src="https://github.com/user-attachments/assets/62fc0016-3808-4a99-93b7-2edd66b226be" />

<img width="1919" height="855" alt="image" src="https://github.com/user-attachments/assets/cedc1b0d-34e9-46fb-a59a-37dd6ea38058" />


# AI Summarizer 
This Django web application allows users to generate high-quality summary of YouTube videos using AI. Simply paste a YouTube link, and the system will:

- Download the video audio
- Transcribe the content using AssemblyAI
- Generate a well-structured blog article using Groq LLaMA 3.3 model
- Save and manage generated blogs in your account

# Key Features
- User Authentication (Signup, Login, Logout)
- YouTube Video Processing: Extracts title & downloads audio using yt-dlp.
- Speech-to-Text: Uses AssemblyAI for transcription.
- AI-Powered Blog Generation: Uses Groq LLaMA 3.3 for high-quality content.
- Asynchronous Task Handling: Implements Celery + Redis for background processing.

# Note: please use two terminals for this project as it use celery for generating blog from the link.
- For terminal1, file_path/project> python manage.py runserver
- For terminal2, file_path/project> celery -A backend worker --pool=solo -l info  ( works for Windows)
