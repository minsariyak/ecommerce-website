from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import *

@login_required(login_url="login")
def index(request):
    listings = Listing.objects.filter(status=True)
    return render(request, "auctions/index.html", {
        "listings": listings
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

@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = float(request.POST.get('price'))
        url = request.POST.get('url')
        category = request.POST.get('category')

        category_obj = Category.objects.get(pk=category)
        new_listing = Listing(title=title, description=description, current_price=price, url=url, category=category_obj, status=True, user=request.user)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            "categories": categories
        })

@login_required(login_url="login")
def close_listing(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        listing.status = False
        listing.save()

        return HttpResponseRedirect(reverse("index"))


@login_required(login_url="login")
def display_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.filter(user=request.user)
    comments = Comment.objects.filter(listing=listing)
    bids = Bid.objects.filter(listing=listing)

    bid_winner = Bid.objects.filter(listing=listing)
    if bid_winner:
        winner = bid_winner.latest('amount')
    else:
        winner = None

    exists_in_watchlist = False
    for list in watchlist:
        if listing.id == list.listing.id:
            exists_in_watchlist = True
            break
        else:
            exists_in_watchlist = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "exists_in_watchlist": exists_in_watchlist,
        "comments": comments,
        "total_bids": len(bids),
        "winner": winner
    })

@login_required(login_url="login")
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required(login_url="login")
def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        watchlist = Watchlist(listing=listing, user=request.user)
        watchlist.save()
        return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))
    else:
        user = User.objects.get(pk=request.user.id)
        watchlist = Watchlist.objects.filter(user=user)
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })

@login_required(login_url="login")
def remove_from_watchlist(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        watchlist = Watchlist.objects.filter(listing=listing, user=request.user)
        watchlist.delete()

        return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))

@login_required(login_url="login")
def categorized_listings(request, cat_id):
    category = Category.objects.get(pk=cat_id)
    listings = Listing.objects.filter(category=category)

    return render(request, "auctions/categorized_listings.html", {
        "listings": listings,
        "category": category
    })

@login_required(login_url="login")
def add_comment(request):
    if request.method =="POST":
        comment = request.POST.get('comment')

        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)

        new_comment = Comment(comment=comment, user=request.user, listing=listing)
        new_comment.save()

        return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))

@login_required(login_url="login")
def place_bid(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id')
        listing = Listing.objects.get(pk=listing_id)
        bid_amount = float(request.POST.get('bid_amount'))

        if bid_amount < listing.current_price:
            messages.error(request, 'Bid needs to be greater than current price.')
            return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))

        bid = Bid.objects.filter(user=request.user, listing=listing)

        if len(bid) > 0:
            bid[0].amount = bid_amount
            bid[0].save()
        else:
            new_bid = Bid(amount=bid_amount, user=request.user, listing=listing)
            new_bid.save()

        listing.current_price = bid_amount
        listing.save()

        return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))






