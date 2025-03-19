from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required, user_passes_test
from fms_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from fmsApp.forms import UserRegistration, SavePost, UpdateProfile, UpdatePasswords
from fmsApp.models import Post
from cryptography.fernet import Fernet
from django.conf import settings
import base64

# Create your views here.
context = {
    'page_title' : 'BSL',
}
#For pages that dont require login 
def tools(request):
    return render(request,'tools.html',context)
def calendar(request):
    return render(request,'calendar.html',context)
# For pages that require login
@login_required
@user_passes_test(lambda u: u.groups.filter(name='reviewer').exists())
def reviewer_dashboard(request):
    posts = Post.objects.all()
    return render(request, 'reviewer_dashboard.html', {'posts': posts})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='reviewer').exists())
def update_status(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        post.status = status
        post.reviewer = request.user
        post.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
@login_required
def portal(request):
    return render(request, 'portal.html',context)

@login_required
def inventory(request):
    return render(request, 'inventory.html')

@login_required
def reports(request):
    return render(request, 'reports.html')
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    next_url = request.GET.get('next', '')  # Get the 'next' parameter from the URL
    
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
                # Redirect to the 'next' URL if it exists, otherwise redirect to the home page
                if next_url:
                    resp['redirect'] = next_url
                else:
                    resp['redirect'] = '/' 
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/login')

@login_required
def training_folder(request):
    context['page_title'] = 'Training'
    if request.user.is_superuser:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(user = request.user).all()
    context['posts'] = posts
    context['postsLen'] = posts.count()
    print(request.build_absolute_uri())
    return render(request, 'training_folder.html',context)


def home(request):
    if isinstance(request.user, AnonymousUser):
        # Handle the case where the user is not authenticated
        context = {
            'page_title': 'Home',
            'posts': [],
            'postsLen': 0
        }
    else:
        context = {
            'page_title': 'Home',
            'posts': Post.objects.filter(user=request.user) if not request.user.is_superuser else Post.objects.all(),
            'postsLen': Post.objects.filter(user=request.user).count() if not request.user.is_superuser else Post.objects.count()
        }
    print(request.build_absolute_uri())
    return render(request, 'home.html', context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html',context)
@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def posts_mgt(request):
    context['page_title'] = 'Uploads'
    posts = Post.objects.filter(user = request.user).order_by('title', '-date_created').all()
    context['posts'] = posts
    return render(request, 'posts_mgt.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def save_post(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if not request.POST['id'] == '':
            post = Post.objects.get(id=request.POST['id'])
            if post.user != request.user:  # Ensure staff can only update their own posts
                resp['msg'] = "You do not have permission to update this post."
                return HttpResponse(json.dumps(resp), content_type="application/json")
            form = SavePost(request.POST, request.FILES, instance=post)
        else:
            form = SavePost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  # Assign the current user as the post owner
            post.save()
            messages.success(request, 'File has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + '<br/>')
    else:
        resp['msg'] = "No Data sent."
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def manage_post(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    if not pk is None:
        post = get_object_or_404(Post, id=pk)
        if post.user != request.user:  # Ensure staff can only manage their own posts
            messages.error(request, "You do not have permission to manage this post.")
            return redirect('posts_mgt')
        context['post'] = post
    return render(request, 'manage_post.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def delete_post(request):
    resp = {'status':'failed', 'msg':''}
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=request.POST['id'])
            if post.user != request.user:  # Ensure staff can only delete their own posts
                resp['msg'] = "You do not have permission to delete this post."
                return HttpResponse(json.dumps(resp), content_type="application/json")
            post.delete()
            resp['status'] = 'success'
            messages.success(request, 'Post has been deleted successfully')
        except:
            resp['msg'] = "Undefined Post ID"
    return HttpResponse(json.dumps(resp), content_type="application/json")

def shareF(request,id=None):
    # print(str("b'UdhnfelTxqj3q6BbPe7H86sfQnboSBzb0irm2atoFUw='").encode())
    context['page_title'] = 'Shared File'
    if not id is None:
        key = settings.ID_ENCRYPTION_KEY
        fernet = Fernet(key)
        id = base64.urlsafe_b64decode(id)
        id = fernet.decrypt(id).decode()
        post = Post.objects.get(id = id)
        context['post'] = post
        context['page_title'] += str(" - " + post.title)
   
    return render(request, 'share-file.html',context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='staff').exists())
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)



