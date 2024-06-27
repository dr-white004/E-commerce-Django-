from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Auctioning, Bid, Comment

present = True

def index(request):
    #to display only active lsting
    entries = Auctioning.objects.filter(checking = True)
    return render(request, "auctions/index.html",{
        'entries': entries
    })

def closedlisting(request):
    entries = Auctioning.objects.filter(checking = False)
    return render(request, "auctions/closed.html",{
        'entries': entries
    })




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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")



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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")      
    else:
        # user = User.objects.get(username=request.user)
        user = request.user
        store = request.POST
        bid = Bid.objects.create(bid = store['bid'], user=user )
        bid.save()
        Auctionlistings = Auctioning.objects.create(title = store['title'], description= store['description'], image = store['img'], category = store['category'] ,price =bid , owner = user, checking=True)
        Auctionlistings.save()        
        global update_owner
        update_owner = user
        return render(request, "auctions/index.html",{
        'entries': Auctioning.objects.all()
        })



def addwatchlist(request, num):
    Data = Auctioning.objects.get(id = num)
    currentuser = request.user
    #check for presence of particular listing
    if currentuser.watch.filter(id=num).exists():
        currentuser.watch.remove(Data)      
        
    else:
        currentuser.watch.add(Data)
    
    return HttpResponseRedirect(reverse("goto", args=(num,)))



def yourwatchlist(request):
    user = request.user #collect username for storage in watchlist model
    return render(request, "auctions/watchlist.html", {
            "watchlist": user.watch.all()
    })



def newbid(request, num):
    entry = Auctioning.objects.get(id = num)
    current = entry.price.bid
    try:
        new = bid = int(request.POST["newbid"])
    except ValueError: 
        return render(request, "auctions/goto.html", {
            "message": "Must input a number",
            "entry": entry,
            "updated": False,
            })

    if new > current:
        change = Bid(bid=new, user=request.user)
        change.save()
        entry.price = change
        entry.save()
        return render(request, "auctions/goto.html", {
            "entry": entry,
            "message": "Bid was updated successfully",
            "updated": True,
            })
    else:
        return render(request, "auctions/goto.html", {
            "message": "New-Bid must be higher than previous bid",
            "entry": entry,
            "updated": False,
            })
 
             


def close_auction(request, num):
    entry = Auctioning.objects.get(pk=num)
    entry.checking = False
    entry.save()
    return HttpResponseRedirect(reverse("goto", args=(num, )))


@login_required(login_url='login')
def goto(request, num): 
    entry = Auctioning.objects.get(id = num) 
    is_owner = request.user.username == entry.owner.username
    currentuser = request.user
    comments = Comment.objects.filter(auction = entry)
    global present

    if currentuser.watch.filter(id=num).exists():
        present = True
    else:
        present = False
    
    if entry.checking == True:       
        return render(request, "auctions/goto.html",{
            'entry': entry,
            'present':present,
            'is_owner':is_owner,
            'comments':comments
        })
    elif entry.checking == False and entry.price.user == request.user:
        return render(request, "auctions/goto.html",{
            'entry': entry,
            'is_owner':is_owner,
            'present':present,
            'update_owner':update_owner,
            'comments':comments
        })
    elif entry.checking == False and entry.price.user != request.user:    
        return render(request, "auctions/goto.html",{
            'entry': entry,
            'is_owner':is_owner,
            'present':present,
            'comments':comments
        })


def comment(request, num):
    commenter = request.user.username
    entry = Auctioning.objects.get(pk=num)
    message = request.POST['newcomment']
    newcomment = Comment.objects.create(author = commenter,  auction = entry, comment = message)
    newcomment.save()
    return HttpResponseRedirect(reverse("goto", args=(num, )))



def category(request):
    categories = Auctioning.objects.all().values_list('category', flat=True).distinct()
    return render(request, "auctions/category.html", {
        "categories": categories
    })


def displaycategory(request, nam):
    content  = Auctioning.objects.filter(category= nam, checking=True)
    return render(request, "auctions/displaycategory.html", {
        "content": content
    })

