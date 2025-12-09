"""
Django Chatbot URL Configuration
"""
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('schema/', views.schema_info, name='schema'),
    path('health/', views.health, name='health'),
]
