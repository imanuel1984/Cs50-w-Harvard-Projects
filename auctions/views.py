from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from decimal import Decimal

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import CreateListingForm, BidForm, CommentForm


# Home page: show all active listings
def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {"listings": listings})


# Authentication
def login_view(request):
    if request.method == "POST":
        username, password = request.POST["username"], request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("index")
        return render(request, "auctions/login.html", {"message": "Invalid username or password."})

    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username, email = request.POST["username"], request.POST["email"]
        password, confirmation = request.POST["password"], request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})

        login(request, user)
        return redirect("index")

    return render(request, "auctions/register.html")


# Create a new listing
@login_required
def create_listing(request):
    form = CreateListingForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        listing = form.save(commit=False)
        listing.owner = request.user
        listing.save()
        messages.success(request, "Listing created!")
        return redirect("listing", listing_id=listing.id)

    return render(request, "auctions/create.html", {"form": form})


# Listing detail (bids, comments, watchlist)


from decimal import Decimal

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_form, comment_form, winner = BidForm(), CommentForm(), None

    # Determine winner if auction is closed
    if not listing.active:
        highest_bid = listing.bids.order_by('-amount').first()
        if highest_bid:
            winner = highest_bid.bidder

    if request.method == "POST":
        action = request.POST.get("action")

        # Handle bids
        if action == "bid":
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to bid.")
                return redirect("login")

            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                amount = Decimal(bid_form.cleaned_data["amount"])
                current_price = Decimal(listing.current_price())  # should also be Decimal

                if amount <= current_price:
                    messages.error(request, f"Bid must be greater than current price (${current_price}).")
                elif not listing.active:
                    messages.error(request, "Auction is closed.")
                else:
                    # Create the bid
                    Bid.objects.create(listing=listing, bidder=request.user, amount=amount)
                    messages.success(request, "Bid placed successfully!")
                    return redirect("listing", listing_id=listing.id)

        # Handle comments
        elif action == "comment":
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to comment.")
                return redirect("login")

            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                Comment.objects.create(
                    listing=listing,
                    author=request.user,
                    text=comment_form.cleaned_data["text"]
                )
                messages.success(request, "Comment added!")
                return redirect("listing", listing_id=listing.id)

    # Check watchlist status
    in_watchlist = request.user.is_authenticated and Watchlist.objects.filter(
        user=request.user, listing=listing
    ).exists()

    # Check if current user can close auction
    can_close = request.user.is_authenticated and request.user == listing.owner and listing.active

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "in_watchlist": in_watchlist,
        "bids": listing.bids.select_related("bidder"),
        "comments": listing.comments.select_related("author"),
        "can_close": can_close,
        "winner": winner,
    })





# Toggle watchlist
@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        obj, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            obj.delete()
            messages.success(request, "Removed from watchlist.")
        else:
            messages.success(request, "Added to watchlist.")
    return redirect("listing", listing_id=listing.id)


# Close auction
@login_required
@transaction.atomic
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.user != listing.owner:
        messages.error(request, "You cannot close someone else’s auction.")
    else:
        listing.active = False
        listing.save()
        messages.success(request, "Auction closed successfully.")
    return redirect("listing", listing_id=listing.id)


# Watchlist page
@login_required
def watchlist(request):
    listings = Listing.objects.filter(watchers__user=request.user)
    return render(request, "auctions/watchlist.html", {"listings": listings})


# Categories
def categories(request):
    cats = [cat[0] for cat in Listing.CATEGORY_CHOICES]
    return render(request, "auctions/categories.html", {"categories": cats})


def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name, active=True)
    return render(request, "auctions/category_list.html", {
        "category": category_name,
        "listings": listings
    })
