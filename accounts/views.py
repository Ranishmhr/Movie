from django.contrib.auth import (
authenticate,
get_user_model,
login,
logout
)
from django.shortcuts import render, redirect
from .forms import UserLoginForm,UserRegisterForm,ReviewForm
from movies.models import Movies

def login_view(request):

    title = "Login Form"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect("/home")
    context = {"form": form,
               "title": title
               }
    return render(request,"form.html",context)

def register_view(request):

    title = "Register Form"
    form = UserRegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.email=form.cleaned_data.get('email')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        #redirect
        return redirect("/home")

    context = {"form":form,
               "title": title
               }
    return render(request,"register.html",context)

def logout_view(request):
    logout(request)
    return redirect("/loginn")

def add_review(request, id):
    if request.user.is_authenticated:
        movie=Movies.objects.get(id=id)
        if request.method == "POST":
            form = ReviewForm(request.POST or None)
            if form.is_valid():
                data=form.save(commit=False)
                data.comment=request.POST["comment"]
                data.rating=request.POST["rating"]
                data.user=request.user
                data.userid=data.user
                data.movieid=movie
                data.save()
                return redirect("movies:detail",id)
        else:
            form = ReviewForm()
        return redirect(request,'detail.html',{"form":form})
    else:
        return redirect("/loginn")
