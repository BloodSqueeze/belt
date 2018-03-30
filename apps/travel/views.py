from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import re, bcrypt
from .models import *
import datetime
from dateutil.parser import parse as parse_date
# Create your views here.
def index(request):
    users = User.objects.all()
    context = {
        'users': users,

    }
    return render(request, 'travel/index.html', context)


def register(request):
    valid = True
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    password = request.POST['password']
    confirm = request.POST['pass_confirm']
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    if request.method == 'POST':
        if len(first_name) < 2:
            valid = False
            messages.error(request, 'First Name needs to be longer than 2 Characters')
        if len(last_name) < 2:
            valid = False
            messages.error(request, 'Last Name needs to be longer than 2 Characters')
        if len(email) < 6:
            valid = False
            messages.error(request, 'Email is required and must be in valid format ex: name@email.com')
        if password != confirm:
            valid = False
            messages.error(request, 'Password does not match!')
        if valid == True:
            try:
                User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed_password)
                user = User.objects.get(email=email)
                request.session['current_user'] = user.id
                print 'user.id---------------------'
                messages.success(request, 'You have registered successfully and are now logged in')
                return redirect('/logged')
            except Exception as problem:
                print problem
                messages.error(request, 'Email already exists')
    return redirect('/')
def login(request):
    email = request.POST['email']
    password = request.POST['password']
    if request.method == 'POST':
        if len(password) > 0:
            try:
                user = User.objects.get(email=email)
                if bcrypt.checkpw(password.encode(), user.password.encode()):
                    request.session['current_user'] = user.id
                    print 'user.id---------------------'
                    messages.success(request, 'You have successfully logged in')
                    request.session['email'] = email
                    current_user = User.objects.get(email=email)
                    request.session['current_user'] = current_user.id
                    return redirect('/logged')
                else:
                    messages.error(request, 'you need to remember your password')
                    return redirect('/')
            except Exception as problem:
                messages.error(request, 'you need to register first')
                print problem
                return redirect('/')
        else:
            messages.error(request, 'you need to submit a password to continue')
            return redirect('/')
    return redirect('/login)')

def logged(request):
    if 'current_user' in request.session:
        context = {
            'user': User.objects.get(id=request.session['current_user']),
            'trips': Plan.objects.filter(enrollee=request.session['current_user']),
            'created_trips': Plan.objects.filter(creator=request.session['current_user']),
            'other_trips': Plan.objects.all().exclude(creator=request.session['current_user']).exclude(enrollee=request.session['current_user'])
        }
    print request.session['current_user'], '******************'
    return render(request, 'travel/trips.html', context)

def logout(request):
    request.session.flush
    return redirect('/')

def add(request):
    return render(request, 'travel/add_form.html')

def create(request):
    valid = True
    destination = request.POST['destination']
    description = request.POST['description']
    start = request.POST['start']
    finish = request.POST['finish']
    user_id = request.session['current_user']
    creator = User.objects.get(id=request.session['current_user'])
    now = datetime.datetime.now()
    if len(destination) < 1:
        valid = False
        print valid
        messages.error(request, 'You cannot submit a blank destination')
    if len(description) < 1:
        valid = False
        messages.error(request, 'You cannot submit a blank description')
    if start < 1:
        valid = False
        messages.error(request, 'You cannot submit a blank start date')
    if len(finish) < 1:
        valid = False
        messages.error(request, 'You cannot submit a blank ending date')
    if len(start) > 1:
        if parse_date(start) <= now:
            valid = False
            messages.error(request, 'Your Trip must start after today')
        if finish <= start:
            valid = False
            messages.error(request, 'Your Trip must last at least 1 day')
    if valid == True:
        Plan.objects.create(destination=destination, description=description, start=start, finish=finish, creator=User.objects.get(id=request.session['current_user']))
        print 'yay *******************'
        return redirect('/logged')
    elif valid == False:
        return redirect('/add')
    return redirect('/logged')

def enroll(request, trip_id):
    user_id = request.session['current_user']
    trip = Plan.objects.get(id=trip_id)
    user = User.objects.get(id=user_id)
    trip.enrollee.add(user)
    trip.save()
    return redirect('/logged')

def show(request, trip_id):
    trip = Plan.objects.get(id=trip_id)
    current_user = User.objects.get(id=request.session['current_user'])
    context = {
        'trip': trip,
        'other_users': User.objects.filter(courses_enrolled=trip).exclude(created_courses=trip.id)
    }
    return render(request, 'travel/show.html', context)
