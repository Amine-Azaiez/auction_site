from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Auction(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default="Other")
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reveal_identity = models.BooleanField(default=True)
    legal_responsibility = models.BooleanField(default=False)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_bidder = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='bids')
    winner_email_sent= models.BooleanField(default=False)
    location_latitude = models.FloatField(null=True, blank=True)
    location_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title



class AuctionPicture(models.Model):
    auction = models.ForeignKey(Auction, related_name='pictures', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='auction_pictures/')

    def __str__(self):
        return f'Picture for {self.auction.title}'

class AuctionVideo(models.Model):
    auction = models.ForeignKey(Auction, related_name='videos', on_delete=models.CASCADE)
    video_url = models.URLField()

    def __str__(self):
        return f'Video for {self.auction.title}'


class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'auction')  # Ensure each user can only favourite an auction once

    def __str__(self):
        return f"{self.user.username} - {self.auction.title}"


class Bid(models.Model):
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"
    
    