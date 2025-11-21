# Voting_System/urls.py  (ROOT — DO NOT TOUCH DJANGO ADMIN)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # ← Rename Django admin to avoid conflicts
    path('', include('voting_app.urls')),
    path('api/', include('voting_app.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)