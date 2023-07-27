from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms 
from datetime import datetime
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


from .models import User, Auction, Comment, Bids, Category

class NewForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'id' : 'titleBox'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    startingBids = forms.IntegerField()
    photoURL = forms.URLField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

class BidForm(forms.Form):
    price = forms.DecimalField(label="Enter your bid", max_digits=10, decimal_places=1, widget=forms.NumberInput(attrs={'step' : '0.5'}))

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

def index(request):
    return render(request, "auctions/index.html", {
        "auctions" : Auction.objects.all()
    })

def users_auction(request):
    auction = Auction.objects.filter(author = request.user)
    return render(request, "auctions/index.html", {
        "auctions" : auction
    })

def categorize(request, category_id):
    category = Category.objects.get(pk=category_id)
    auctions = Auction.objects.filter(category = category)
    return render(request, "auctions/index.html", {
        "auctions" : auctions
    })

def create_comment(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = comment_form.cleaned_data['text']
            comment = Comment(content=text, auction=auction, user=request.user)
            comment.save()
            return HttpResponseRedirect(reverse('auction', args=[auction_id]))
    
    return HttpResponseRedirect(reverse_lazy('auction', args=[auction_id]))

def auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)  
    comments = Comment.objects.filter(auction=auction) 

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            price = form.cleaned_data['price']
            if price > auction.price:
                bid = Bids(auction = auction, bidder = request.user, price = price)
                bid.save()
                auction.price = price
                print(price)
                auction.save()
                return HttpResponseRedirect(reverse('auction', args=[auction_id]))

            else:
                form.add_error('price', "Your bid must be higher than the current price.")
        else:
            form = BidForm()

    return render(request, "auctions/auction.html", {
        "auction" : Auction.objects.get(pk=auction_id),
        "form" : BidForm(initial={"price" : auction.price}),
        "comment_form" : CommentForm(),
        "comments" : comments,
        "watching": auction in request.user.watchlist.all()
    })

def close_auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)  
    auction.active = False
    auction.save()
    return HttpResponseRedirect(reverse('auction', args=[auction_id]))

    

@login_required
def watchlist(request, user_id):
    user = User.objects.get(pk=user_id)
    return render(request, "auctions/watchlist.html", {
        "watchlist" : user.watchlist.all()
    })

@login_required
def update_watchlist(request, auction_id, update):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    if update == "remove":
        user.watchlist.remove(auction)
    elif update == "add":
        user.watchlist.add(auction)
    return HttpResponseRedirect(reverse('auction', args=[auction_id]))




def create(request, user_id):
    if (request.method == "POST"):
        currForm = NewForm(request.POST)
    
        if (currForm.is_valid()):

            title = currForm.cleaned_data["title"]
            description = currForm.cleaned_data["description"]
            startingBids = currForm.cleaned_data["startingBids"]
            photoURL = currForm.cleaned_data["photoURL"]
            
            new_auction = Auction(
                title=title,
                description=description,
                startingBids=startingBids,
                photoURL=photoURL,
                author=User.objects.get(pk=user_id),
                highestbidder=User.objects.get(pk=user_id)
            )
            new_auction.save()
            return redirect(index)
    return render(request, "auctions/create.html", {
        "form" : NewForm(),
        "message" : ""
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
