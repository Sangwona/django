from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment')
    content = models.CharField(max_length=200)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='comments', null = True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Auction(models.Model):    
    title = models.CharField(max_length=64)
    description = models.TextField()
    startingBids = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=1)
    photoURL = models.URLField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions_created')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    highestbidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winning_auctions')
    active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='auctions', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Save an initial price which has the same value as startingBids
        if not self.pk:
            self.price = self.startingBids
        super().save(*args, **kwargs)

    # optional category

    def __str__(self):
        return f"{self.id}: title : {self.title} with starting bid {self.startingBids}"
    
class Bids(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

class Category(models.Model):
    title = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.title}"


