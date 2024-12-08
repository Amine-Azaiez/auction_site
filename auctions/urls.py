from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # Home view for the root URL
    path('about_us/', views.about_us, name='about_us'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('auction_list/', views.auction_list, name='auction_list'),
    path('auction/<int:pk>/', views.auction_detail, name='auction_detail'),
    path('auction/<int:pk>/submit_bid/', views.submit_bid, name='submit_bid'),
    path('auction/add/', views.add_auction, name='add_auction'),
    path('auction/<int:auction_id>/favourite/', views.toggle_favourite, name='toggle_favourite'),
    
    
]


