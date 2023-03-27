from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User,UserPW
from django.db.models import Q
from .forms import *
from django.shortcuts import render

#render home screen as default
def home_page(request):
    return render(request, 'index.html')

def register_page(request):
    #Use the Registration form from forms.py
    form = RegisterForm(request.POST or None)
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in as  %s " % request.user + " you can't register or login ones already logged in!")
        return redirect(home_page)
        #check if valid if so create a user otherwise raise an exeption
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        try:
            user = User.objects.create_user(username, email, password)
        except:
            user = None
        if user != None:
            login(request, user)
            return redirect(user_pw_all)
        else:
            request.session['register_error'] = 1 # 1 == True
    return render(request, "register.html", {"form": form})


def login_page(request):
    form = LoginForm(request.POST or None)
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in as %s" % request.user + " you can't register or login ones already logged in!")
        return redirect(user_pw_all)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user != None:
            login(request, user)
            return redirect(user_pw_all)
        else:
            messages.warning(request, 'Please enter the right password!')
    return render(request, "login.html", {"form": form})
  
#The @login_required decorator checks if user is logged in otherwise you can't access the logout page.
@login_required(login_url=login_page)
def logged_out_page(request):
    logout(request)
    return render(request, "logout.html")

@login_required(login_url=login_page)
def user_pw_all(request):
    if request.user.is_authenticated:
        messages.success(request, "Logged in as %s" % request.user)
    logged_in_user = request.user  
    logged_in_user_pws = UserPW.objects.filter(user=logged_in_user).order_by('-date')
    if not logged_in_user_pws:
        message = 'Please create a password'
        return render(request, "user_pw_all.html", {'no_pws': message})
    
    return render(request, "user_pw_all.html", {'pws': logged_in_user_pws})
    
@login_required
def edit_post(request, pk):
    user_post = UserPW.objects.get(id=pk)
    form = UserUpdateForm(instance=user_post)
    
    if request.method == 'POST':
        form =UserUpdateForm(request.POST, instance=user_post)
        if form.is_valid():
            form.save()
            return redirect('/')
    
    context = {'form': form}

    return render(request, 'edit.html', context)


@login_required
def delete(request, pk):
    user_post = UserPW.objects.get(id=pk)
    
    if request.method == 'POST':
        user_post.delete()
        return redirect('/')
    
    # context = {'item': user_post} 

    return redirect(home_page)


@login_required(login_url=login_page)
def user_pw_add(request):
    form = UserPWForm(request.POST or None)
    if request.user.is_authenticated:
        messages.success(request, "Logged in as %s" % request.user)
    logged_in_user = request.user
    if form.is_valid():
        title = form.cleaned_data.get("title")
        password = form.cleaned_data.get("password")
        # type = form.cleaned_data.get("type")
        if UserPW.objects.filter(title=title) and UserPW.objects.filter(user=request.user):
            messages.success(request, "There is already a pw created by that name")
        else:
            try:
                UserPW.objects.create(title=title, password=password, user=logged_in_user)
                messages.success(request, "Sucessfully added new pw field for your storage")
            except Exception as e:
                raise e
        return redirect(user_pw_all)
    context={
        'form':form
    }        
    return render(request, "user_pw_add.html",context)
 
@login_required(login_url=login_page)
def user_pw_search(request):
    if request.user.is_authenticated:
        messages.success(request, "Logged in as %s" % request.user)
    logged_in_user = request.user  
    logged_in_user_pws = UserPW.objects.filter(user=logged_in_user)
    if request.method == "POST":
        searched = request.POST.get("password_search", "")
        users_pws = logged_in_user_pws.values()
        if users_pws.filter(title=searched):
            user_pw = UserPW.objects.filter(Q(title=searched)).values()
            return render(request, "user_pw_search.html", {'user_pw': user_pw})
        else:
            messages.error(request, "YOUR SEARCH RESULT DOESN'T EXIST")
   

    return render(request, "user_pw_search.html", {'pws': logged_in_user_pws})