"""
Django Project URL Configuration
"""
from django.urls import path, include

urlpatterns = [
    path('api/chatbot/', include('chatbot.urls')),
    path('api/ignis-ai/', include('ignis.urls')),
]
