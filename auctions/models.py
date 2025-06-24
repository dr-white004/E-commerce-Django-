from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Bid(models.Model):
    bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")

    def __str__(self):
        return f"{self.bid}$ from {self.user}"


class Auctioning(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=100)
    image = models.URLField(max_length=200) 
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="price", default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True, blank=True)
    checking = models.BooleanField(default=False, blank=True, null=True)
    category = models.CharField(max_length=400, null=True, blank=True)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watch")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_auctions")

    def __str__(self):
        return f"{self.title}: {self.price}"


class Comment(models.Model):
    author = models.CharField(max_length=64)
    comment = models.CharField(max_length=64)
    auction = models.ForeignKey(Auctioning, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.comment}"