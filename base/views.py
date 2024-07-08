from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm, MyUserCreationForm
from django.db.models import Q
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
# from django.contrib.auth.forms import UserCreationForm

# from django.http import HttpResponse

# rooms = [
#    {
#       'id':1, 'name':"Let's learn python"
#    },
#     {
#       'id':2, 'name':"Design with me"
#    }
#    ,
#     {
#       'id':3, 'name':"Frontend Developer"
#     }
# ]

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')
    if(request.method == "POST"):
        # username = request.POST.get('email').lower()
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email = email)
           
            # print("The user is ", user)
        except Exception as e:
            messages.error(request, "User Does not Exist")
            print("The exception is ", e)
        user = authenticate(request,email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request,"Logged in successfully")
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is not Valid')
    context = {'page': page}
    return render(request,'base/login_register.html',context)
    # return render(request,'base/login.html',context)

def registerPage(request):
    # form = UserForm()
    # form = UserCreationForm()
    try:
        form = MyUserCreationForm()

        if request.method == 'POST':
            # form = UserCreationForm(request.POST)
            form = MyUserCreationForm(request.POST)
            # form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request,user)
                return redirect('home')
            # else:
            #     messages.error(request,"An error occured during registration")
    except Exception as e:
        messages.error(request,"An error occured during registration" + e)
        # print(e)
        return redirect('register')
    return render(request,'base/login_register.html',{'form':form})

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    search = request.GET.get('topic') if request.GET.get('topic') != None else ''
    print(search , "=========")
    rooms = Room.objects.filter(
        Q(topic__name__icontains = search) |
        Q(name__icontains = search) |
        Q(description__icontains = search)
        )
    # rooms = Room.objects.all()
    topic = Topic.objects.all()[0:5]
    room_count = rooms.count()
    # room_messages = Message.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = search))

    context = {'rooms': rooms,'topics':topic, 'room_count' : room_count,'room_messages':room_messages }
    return render(request,'base/home.html', context)
  # return HttpResponse("Home page")
  # return render(request,'home.html',{'rooms':rooms})

def room(request,pk):
    # print(pk)
    # room = None 
    # for single_room in rooms:
    #    if(single_room['id'] == int(pk)):
    #       room = single_room
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    try:
        if(request.method == 'POST'):
            if request.user.is_authenticated:
                message = Message.objects.create(
                user = request.user,
                room = room,
                body = request.POST.get('body') 
                )
                room.participants.add(request.user)
                return redirect('room', pk = room.id)
            else:
                messages.error(request,"You must login to write a message")
                return redirect("login")
    except Exception as e:
        print(e)
        messages.error(request,str(e))
        return redirect('room', pk = room.id)


    
    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    print(pk)
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    page = 'create-room'
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        print(request.POST)
        topic_name = request.POST.get('topic');
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            topic = topic,
            host = request.user,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        );
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #   room = form.save(commit = False)
        #   room.host = request.user
        #   room.save()
        return redirect('home')

    context = {'form': form,'topics':topics,'page':page}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    print(room)
    form = RoomForm(instance = room)

    if request.user != room.host:
        return HttpResponse("You are not allowed here !!")
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid:
        #     form.save()
        #     return redirect('home')
    context = {'form' : form,'room':room}
    print(context,"=============")
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here !!")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    # room = Room.objects.get(id=pk)
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed here !!")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance = user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk = user.id)
    context = {'form':form}
    return render(request,'base/edit-user.html',context)

def topicPage(request):
    # search = Topic.objects.get('topic') if Topic.objects.get('topic') != None else ''
    search = request.GET.get('topic') if request.GET.get('topic') != None else ''
    topics = Topic.objects.filter(name__icontains = search)
    context = {'topics':topics}
    return render(request,'base/topics.html',context)

def activitiyPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request,'base/activity.html',context)



