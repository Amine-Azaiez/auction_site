from django.contrib import admin
from .models import Auction, AuctionPicture, AuctionVideo,Favourite,Bid
from django_celery_beat.models import PeriodicTask

# Register your models here.
admin.site.register(Auction)
admin.site.register(AuctionPicture)
admin.site.register(AuctionVideo)
admin.site.register(Favourite)
admin.site.register(Bid)





