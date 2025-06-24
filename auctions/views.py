from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import User, Auctioning, Bid, Comment

def landing(request):
    return render(request, "auctions/landing.html")

def index(request):
    entries = Auctioning.objects.filter(checking=True)
    return render(request, "auctions/index.html", {
        'entries': entries
    })

def closedlisting(request):
    entries = Auctioning.objects.filter(checking=False)
    return render(request, "auctions/closed.html", {
        'entries': entries
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))  # Redirects to /auctions/
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("landing"))  # Redirects to /auctions/

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))  # Redirects to /auctions/
    else:
        return render(request, "auctions/register.html")

def create(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return render(request, "auctions/create.html", {"message": "Must be logged in"})
        store = request.POST
        try:
            bid = int(store['bid'])
            if bid <= 0:
                raise ValueError("Bid must be positive")
            title = store['title'].strip()
            if not title or len(title) > 32:
                raise ValueError("Title must be 1-32 characters")
            description = store['description'].strip()
            if len(description) > 100:
                raise ValueError("Description too long")
            category = store.get('category', '').strip()
            if len(category) > 400:
                raise ValueError("Category too long")
            img = store.get('img', '')
            if img and len(img) > 200:
                raise ValueError("Image URL too long")
        except (ValueError, KeyError) as e:
            return render(request, "auctions/create.html", {"message": str(e)})
        bid_obj = Bid.objects.create(bid=bid, user=user)
        auction = Auctioning.objects.create(
            title=title,
            description=description,
            image=img,
            category=category,
            price=bid_obj,
            owner=user,
            checking=True
        )
        return HttpResponseRedirect(reverse("index"))  # Redirects to /auctions/
    return render(request, "auctions/create.html")

def addwatchlist(request, num):
    try:
        Data = Auctioning.objects.get(id=num)
        currentuser = request.user
        if currentuser.is_authenticated:
            if currentuser.watch.filter(id=num).exists():
                currentuser.watch.remove(Data)
            else:
                currentuser.watch.add(Data)
    except Auctioning.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse("goto", args=(num,)))

def yourwatchlist(request):
    user = request.user
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watch.all() if user.is_authenticated else []
    })

def newbid(request, num):
    try:
        entry = Auctioning.objects.get(id=num)
    except Auctioning.DoesNotExist:
        return render(request, "auctions/index.html", {
            "message": "Auction not found",
            'entries': Auctioning.objects.filter(checking=True)
        })
    current = entry.price.bid
    if not entry.checking:
        return render(request, "auctions/goto.html", {
            "message": "Auction is closed",
            "entry": entry,
            "updated": False,
            'present': request.user.watch.filter(id=num).exists() if request.user.is_authenticated else False,
            'is_owner': request.user == entry.owner if request.user.is_authenticated else False,
            'comments': Comment.objects.filter(auction=entry)
        })
    if not request.user.is_authenticated:
        return render(request, "auctions/goto.html", {
            "message": "Must be logged in to bid",
            "entry": entry,
            "updated": False,
            'present': False,
            'is_owner': False,
            'comments': Comment.objects.filter(auction=entry)
        })
    if request.method == "POST":
        try:
            new = int(request.POST["newbid"])
            if new <= current:
                raise ValueError("Bid must be higher than current bid")
            if new <= 0:
                raise ValueError("Bid must be positive")
        except (ValueError, KeyError):
            return render(request, "auctions/goto.html", {
                "message": "Invalid bid amount",
                "entry": entry,
                "updated": False,
                'present': request.user.watch.filter(id=num).exists(),
                'is_owner': request.user == entry.owner,
                'comments': Comment.objects.filter(auction=entry)
        })
        change = Bid(bid=new, user=request.user)
        change.save()
        entry.price = change
        entry.save()
        return render(request, "auctions/goto.html", {
            "entry": entry,
            "message": "Bid updated successfully",
            "updated": True,
            'present': request.user.watch.filter(id=num).exists(),
            'is_owner': request.user == entry.owner,
            'comments': Comment.objects.filter(auction=entry)
        })
    return render(request, "auctions/goto.html", {
        "entry": entry,
        'present': request.user.watch.filter(id=num).exists() if request.user.is_authenticated else False,
        'is_owner': request.user == entry.owner if request.user.is_authenticated else False,
        'comments': Comment.objects.filter(auction=entry)
    })

def close_auction(request, num):
    try:
        entry = Auctioning.objects.get(pk=num)
    except Auctioning.DoesNotExist:
        return render(request, "auctions/index.html", {
            "message": "Auction not found",
            'entries': Auctioning.objects.filter(checking=True)
        })
    if request.user != entry.owner:
        return render(request, "auctions/goto.html", {
            "message": "Only the owner can close this auction",
            "entry": entry,
            'present': request.user.watch.filter(id=num).exists() if request.user.is_authenticated else False,
            'is_owner': False,
            'comments': Comment.objects.filter(auction=entry)
        })
    entry.checking = False
    entry.winner = entry.price.user if entry.price else None
    entry.save()
    return HttpResponseRedirect(reverse("goto", args=(num,)))

@login_required(login_url='login')
def goto(request, num): 
    try:
        entry = Auctioning.objects.get(id=num)
    except Auctioning.DoesNotExist:
        return render(request, "auctions/index.html", {
            'entries': Auctioning.objects.filter(checking=True),
            'message': 'Auction not found'
        })
    is_owner = request.user.username == entry.owner.username if entry.owner else False
    currentuser = request.user
    comments = Comment.objects.filter(auction=entry)
    present = currentuser.watch.filter(id=num).exists() if currentuser.is_authenticated else False
    context = {
        'entry': entry,
        'present': present,
        'is_owner': is_owner,
        'comments': comments
    }
    if not entry.checking and entry.winner == request.user:
        context['message'] = 'Congratulations! You won this auction!'
    return render(request, "auctions/goto.html", context)

def comment(request, num):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    try:
        entry = Auctioning.objects.get(pk=num)
    except Auctioning.DoesNotExist:
        return render(request, "auctions/index.html", {
            'entries': Auctioning.objects.filter(checking=True),
            'message': 'Auction not found'
        })
    message = request.POST.get('newcomment', '').strip()
    if not message or len(message) > 64:
        return render(request, "auctions/goto.html", {
            "message": "Comment must be 1-64 characters",
            "entry": entry,
            'present': request.user.watch.filter(id=num).exists(),
            'is_owner': request.user == entry.owner,
            'comments': Comment.objects.filter(auction=entry)
        })
    newcomment = Comment.objects.create(
        author=request.user.username,
        auction=entry,
        comment=message
    )
    return HttpResponseRedirect(reverse("goto", args=(num,)))

def category(request):
    categories = Auctioning.objects.all().values_list('category', flat=True).distinct()
    return render(request, "auctions/category.html", {
        "categories": categories
    })

def displaycategory(request, nam):
    content = Auctioning.objects.filter(category=nam, checking=True)
    return render(request, "auctions/displaycategory.html", {
        "content": content
    })

def search_auctions(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    status = request.GET.get('status', 'all')

    auctions = Auctioning.objects.all()
    if query:
        auctions = auctions.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        auctions = auctions.filter(category=category)
    if min_price:
        auctions = auctions.filter(price__bid__gte=min_price)
    if max_price:
        auctions = auctions.filter(price__bid__lte=max_price)
    if status == 'active':
        auctions = auctions.filter(checking=True)
    elif status == 'closed':
        auctions = auctions.filter(checking=False)

    categories = Auctioning.objects.values_list('category', flat=True).distinct()
    return render(request, 'auctions/search.html', {
        'entries': auctions,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'status': status,
    })

def profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'auctions/index.html', {
            'entries': Auctioning.objects.filter(checking=True),
            'message': 'User not found'
        })
    return render(request, 'auctions/profile.html', {
        'profile_user': profile_user,
        'auctions': Auctioning.objects.filter(owner=profile_user),
        'bids': Bid.objects.filter(user=profile_user),
        'watchlist': profile_user.watch.all(),
        'won_auctions': Auctioning.objects.filter(winner=profile_user, checking=False)
    })