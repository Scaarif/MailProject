from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse 
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from .models import User, Post, Profile


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, "network/index.html", {"posts": posts})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
@csrf_exempt
def addpost(request):
    if request.method == "POST":
        post = request.POST.get("post")
        if len(post) != 0:
            obj = Post()
            obj.post = post 
            obj.user = request.user 
            obj.save()
            context = {
            "status": 201,
            "post_id": obj.id,
            "user_id": request.user.id,
            "timestamp": obj.timestamp.strftime("%B %d, %Y, %I:%M %p"),
            }
            return JsonResponse(context, status=201)
    return JsonResponse({},status=400)

@login_required
@csrf_exempt
def editpost(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        new_post = request.POST.get("post")
        try:
            post = Post.objects.get(id=post_id)
            if post.user == request.user: 
                post.post = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get("id")
        is_liked = request.POST.get("is_liked")
        try:
            post = Post.objects.get(id=post_id)
            if is_liked =="no":
                post.like.add(request.user)
                is_liked = "yes"
            elif is_liked == "yes":
                post.like.remove(request.user)
                is_liked = "no"
            post.save()
            return JsonResponse({"likes": post.like.count(), "is_liked": is_liked, "status": 201})
        except:
            return JsonResponse({"error": "Post Not Found", "status": 404})
    return JsonResponse({}, status=400)

@login_required
def profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        users_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        users_profile = Profile.objects.create(user=request.user)
        #return render(request, 'network/profile.html', {"error": True})
    posts = Post.objects.filter(user=user).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    if request.GET.get("page") !=0:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    context = {
    "posts": posts,
    "user": user,
    "profile": profile,
    "users_profile": users_profile
    }
    return render(request, 'network/profile.html', context)

@login_required
@csrf_exempt
def follow(request):
    if request.method == "POST":
        user = request.POST.get("user")
        action = request.POST.get("action")

        user = User.objects.get(username=user)
        I_user = request.user

        if action == "Follow":
            try:
                #Add user to current user's following list
                profile = Profile.objects.get(user=I_user)
                profile.following.add(user)
                profile.save()

                #Add current user to user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.add(I_user)
                profile.save()

                return JsonResponse({"status": 201,
                    "action":"Unfollow",
                    "followers": profile.follower.count()},
                    status=201)
            except:
                return JsonResponse({}, status=404)

        else: #ie action == "Unfollow":
            try:
                #Remove user from current user's following list
                profile = Profile.objects.get(user=I_user)
                profile.following.remove(user)
                profile.save()

                #Remove current user from user's follower list
                profile = Profile.objects.get(user=user)
                profile.follower.remove(I_user)
                profile.save()

                return JsonResponse({"status":201, "action":"Follow", "followers":profile.follower.count()},
                    status=201)
            except:
                return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)

@login_required
def following(request):
    following = Profile.objects.get(user=request.user).following.all()
    posts = Post.objects.filter(user__in=following).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != 0:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, "network/following.html", {"posts":posts})



