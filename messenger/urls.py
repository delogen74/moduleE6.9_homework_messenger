from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .consumers import ChatConsumer
from . import views

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.users_list, name='users'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_room, name='chat_room'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('create-chat/', views.create_chat, name='create_chat'),
    path('api/', include(router.urls)),
    path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)