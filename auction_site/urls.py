from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('auctions/', include('auctions.urls')),
    path('', include('auctions.urls')),  # This might cause issues, ensure proper URL configuration
]

# Serve media files from /auction_pictures/ during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)