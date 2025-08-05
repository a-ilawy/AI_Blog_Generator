import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from pytube import YouTube
import os
import assemblyai as aai
from django.views.decorators.csrf import csrf_exempt
from pytube.exceptions import VideoUnavailable
from urllib.error import HTTPError


# Create your views here.
@login_required
def home(request):
    return render(request, 'index.html',{})

def loginView(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request=request,username=username, password=password)
        print(user)
        if user:
            login(request, user)
            return redirect('/')
        else:
             return render(request, 'signup.html',{'err_msg':"Invalid Username or password"})
    return render(request, 'login.html',{})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repearPass = request.POST.get('repeatpassword')
        print(f"username: {username} || email: {email} || password: {password} || repearPass: {repearPass} || ")
        if password!=repearPass:
             return render(request, 'signup.html',{'err_msg':"The password does not match."})
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return redirect('/')
        except:
            return render(request, 'signup.html',{'err_msg':"Error creating account"})
    
    return render(request, 'signup.html',{})

def logoutView(request):
    logout(request=request)
    return redirect('/login')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        try:
            title = yt_title(yt_link)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # # use OpenAI to generate the blog
        # blog_content = generate_blog_from_transcription(transcription)
        # if not blog_content:
        #     return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # # save blog article to database
        # new_blog_article = BlogPost.objects.create(
        #     user=request.user,
        #     youtube_title=title,
        #     youtube_link=yt_link,
        #     generated_content=blog_content,
        # )
        # new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': transcription})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

   
def yt_title(link):
    try:
        yt = YouTube(link)
        return yt.title
    except VideoUnavailable:
        raise ValueError("The video is unavailable (private, removed, or restricted).")
    except HTTPError as e:
        raise ValueError(f"YouTube returned an HTTP error: {e.code}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path= settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = ""
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text