from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
   