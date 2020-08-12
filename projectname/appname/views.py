from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, CustomUser, Hashtag
from .forms import PostForm, SigninForm,UserForm,CommentForm, HashtagForm

#from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponse

# Create your views here.
def mypage(request):
    suho = Post.objects.all()
    sooho = CommentForm()
    return render(request, 'appname/mypage.html',{'posts':suho,'comment_form':sooho})

def main(request):
    posts = Post.objects.all()
    hashtags = Hashtag.objects.all()
    signin_form = SigninForm()
    comment_form = CommentForm()
    return render(request, 'appname/main.html', {'posts': posts, 'signin_form': signin_form,
    'comment_form': comment_form, 'hashs':hashtags})
def create(request):
    if not request.user.is_active:
        return HttpResponse("Can't write a post without Sign In")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.writer = request.user

            hashtag_field = form.cleaned_data['hashtag_field']
            str_hashtags = hashtag_field.split('#')
            list_hashtags = list()

            for hashtag in str_hashtags:
                if Hashtag.objects.filter(name=hashtag):
                    list_hashtags.append(Hashtag.objects.get(name=hashtag))
                else:
                    temp_hashtag = HashtagForm().save(commit = False)
                    temp_hashtag.name = hashtag
                    temp_hashtag.save()
                    list_hashtags.append(temp_hashtag)

            post.save()
            post.hashtags.add(*list_hashtags)

            return redirect('main')
    else:
        form = PostForm()
        return render(request, 'appname/create.html', {'form': form})

def read(request):
    return redirect('main')

def update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form = form.save(commit=False)
            form.save()
            return redirect('main')
    else:
        form = PostForm(instance=post)
        return render(request, 'appname/create.html', {'form': form})

def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('main')

def comment(request, post_id):
    suho = Post.objects.all()
    if not request.user.is_active:
        return HttpResponse("Can't write a comment without Sing In")
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
     form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.c_writer = request.user
        comment.post_id = post
        comment.text = form.cleaned_data['text']
        comment.save()
    return redirect('main')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return HttpResponse("로그인 실패. 다시 시도해보세요")
    else:
        signin_form = SigninForm()
        return render(request, 'appname/signin.html', {'signin_form': signin_form})


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = CustomUser.objects.create_user(username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            nickname=form.cleaned_data['nickname'],
            phone_number=form.cleaned_data['phone_number'])
            login(request, new_user)
            return redirect('signup')
    else:
        form = UserForm()
        return render(request, 'appname/signup.html', {'form': form})

def hashtag(request, hashtag_name):
    hashtag = get_object_or_404(Hashtag, name = hashtag_name)
    return render(request, 'appname/hashtag.html', {'hashtag': hashtag})

def like(request, pk):
    if not request.user.is_active:
        return HttpResponse('First SignIn please')

    post = get_object_or_404(Post, pk=pk)
    user = request.user
    
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
    else:
        post.likes.add(user)

    return redirect('main')

