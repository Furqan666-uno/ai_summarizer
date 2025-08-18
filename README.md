<img width="1919" height="838" alt="Screenshot 2025-08-18 215631" src="https://github.com/user-attachments/assets/b9e50b72-a08c-4a61-9338-e49ab6e6a4aa" />

<img width="1919" height="835" alt="Screenshot 2025-08-18 215921" src="https://github.com/user-attachments/assets/af1abf84-a84f-40ae-ad3e-eff281240e40" />

<img width="1919" height="842" alt="Screenshot 2025-08-18 215936" src="https://github.com/user-attachments/assets/523ecb18-9f90-4e77-99aa-72ba7daa3245" />

<img width="1919" height="847" alt="Screenshot 2025-08-18 215955" src="https://github.com/user-attachments/assets/13fd8237-51c4-4ef4-b33a-bf0b51bd406f" />



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
