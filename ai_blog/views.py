from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost
from .tasks import generate_blog_task
from .utils import clean_youtube_link, yt_title, download_audio
from django.http import JsonResponse
from django.conf import settings
from django.http import FileResponse
from urllib.parse import urlparse, parse_qs
from celery.result import AsyncResult
import subprocess
from groq import Groq
import json
import os
import assemblyai as aai 
import yt_dlp


@login_required
def index_page(request):
    return render(request, 'index.html')


def signup_page(request):
    if request.method=="POST":
        form= UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('login')
        else:
            print(form.errors)
    else:
        form= UserRegistrationForm()
    return render(request, 'signup.html', {'form':form})

# ------- we can also create login and logout page this this ------------- 

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from .forms import UserRegistrationForm
# from django.contrib.auth.forms import AuthenticationForm

# def login_view(request):
#     if request.method == "POST":
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, f"Welcome {username}!")
#                 return redirect('home')  # Redirect to homepage or dashboard
#         messages.error(request, "Invalid username or password.")
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})

# def logout_view(request):
#     logout(request)
#     messages.info(request, "You have successfully logged out.")
#     return redirect('login')

# ------------------- but for now we are using LoginView and LogoutView from urls.py ------------------


@csrf_protect # bcz in index.html, in script tag we are making POST request, we need csrf for security
def generate_blog(request):
    if request.method=="POST":
        try:
            data= json.loads(request.body) # here body from index.html, script tag
            yt_link = data.get('link', '').strip()
            yt_link = clean_youtube_link(yt_link)
            print("Cleaned YouTube link:", yt_link)
            
            if not yt_link.startswith("http"):
                return JsonResponse({"error": "Invalid YouTube URL"}, status=400)
        
            task = generate_blog_task.delay(yt_link, request.user.id)
            return JsonResponse({"task_id": task.id})
            # title= yt_title(yt_link) # get youtube title
            # if not title:
            #     return JsonResponse({"error": "Could not fetch YouTube title"}, status=500)
            
            # transcription= get_transcription(yt_link) # get transcription 
            # if not transcription:
            #     return JsonResponse({"error":"Failed to transcribe"}, status=500) 
            
            # blog_content= generate_blog_from_transcription(transcription)
            # if not blog_content:
            #     return JsonResponse({"error":"Failed to generate blog article"}, status=500)
            
            # new_blog_article= BlogPost.objects.create(
            #     user= request.user, youtube_title= title, youtube_link= yt_link, generated_content= blog_content
            # )
            # new_blog_article.save()
            
            # return JsonResponse({"title": title, "content":blog_content})
    
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            print("Unexpected error:", e)
            return JsonResponse({"error": "Internal server error"}, status=500)

    return JsonResponse({"error":"Invalid request method"}, status=405)


# ----------------- this part of code is shifted to utils.py to prevent error ----------------- 
# def yt_title(link):
#     try:
#         # ydl_opts= {'quiet': True}
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'outtmpl': f'{settings.MEDIA_ROOT}/%(title)s.%(ext)s',
#             'ffmpeg_location': r"C:\Users\Dell\Downloads\ffmpeg-2025-07-12-git-35a6de137a-full_build\ffmpeg-2025-07-12-git-35a6de137a-full_build\bin",
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#         }
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(link, download=False)
#             return info.get('title')
#     except Exception as e:
#         print("yt_dlp error (title):", e)
#         return None
    

# def clean_youtube_link(link): # use this in get_blog()
#     # If it's a youtu.be link, extract the video ID
#     if "youtu.be" in link:
#         video_id = link.split("/")[-1].split("?")[0]
#         return f"https://www.youtube.com/watch?v={video_id}"
    
#     # If it's a normal YouTube link with extra params
#     if "youtube.com" in link:
#         parsed = urlparse(link)
#         qs = parse_qs(parsed.query)
#         if "v" in qs:
#             return f"https://www.youtube.com/watch?v={qs['v'][0]}"
#     return link


# def download_audio(link):
#     output_dir= settings.MEDIA_ROOT  # Where you want to store audio
#     audio_path= os.path.join(output_dir, "%(title)s.%(ext)s")  # Auto rename with title

#     ydl_opts= {
#         'format': 'bestaudio/best',
#         'outtmpl': audio_path,
#         'quiet': True,
#         'postprocessors': [
#             {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
#         ]
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(link, download=True)
#             mp3_file = os.path.join(output_dir, f"{info['title']}.mp3")
#             return mp3_file
#     except Exception as e:
#         print("yt_dlp error (audio):", e)
#         return None
# ---------------------------------------------------------------------------------


def get_transcription(link):
    audio_file= download_audio(link)
    aai.settings.api_key= settings.AAI_API_KEY
    transcriber= aai.Transcriber()
    transcript= transcriber.transcribe(audio_file)
    return transcript.text


def generate_blog_from_transcription(transcription):
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        prompt = f"""
        Based on the following transcript from a YouTube video, write a comprehensive blog article.
        Make it professional, well-structured, and not like a YouTube script.

        Transcript:
        {transcription}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",    # Best model for blogs
            messages=[
                {"role": "system", "content": "You are an expert blog writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Groq API Error:", e)
        return None
    

def blog_list(request):
    query= request.GET.get('q', '') # Search query given by form method=GET in blog-list.html
    blog_article= BlogPost.objects.filter(user=request.user)
    if query:
        blog_article= blog_article.filter(Q(youtube_title__icontains=query) | Q(generated_content__icontains=query))

    paginator= Paginator(blog_article.order_by('-id'), 8) # 8 blogs per page 
    page_number= request.GET.get('page')
    page_obj= paginator.get_page(page_number)

    return render(request, "blog-list.html", {"page_obj": page_obj, "query": query})


def blog_details(request, pk):
    blog_article_detail= BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, "blog-details.html", {"blog_article_detail":blog_article_detail})
    return redirect('/')


def blog_delete(request, pk):
    del_blog= BlogPost.objects.filter(id=pk)
    del_blog.delete()
    return redirect('blog-list')


def download_audio_file(request, pk):
    blog = BlogPost.objects.get(id=pk)
    link = blog.youtube_link

    output_dir = settings.MEDIA_ROOT
    file_path = None

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = os.path.join(output_dir, f"{info['title']}.mp3")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"{info['title']}.mp3")


def download_video_file(request, pk):
    blog = BlogPost.objects.get(id=pk)
    link = blog.youtube_link

    output_dir = settings.MEDIA_ROOT
    file_path = None

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = os.path.join(output_dir, f"{info['title']}.mp4")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"{info['title']}.mp4")


def check_status(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        "state": result.state,
        "progress": result.info if isinstance(result.info, str) else "",
        "data": {}
    }
    if result.state == "SUCCESS":
        response_data["data"] = result.result  # Full result from task
    return JsonResponse(response_data)
