from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MessageViewSet, TaskViewSet,frontend,register_page, register_user

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', frontend, name='home'),               # HTML page at root
    path('api/', include(router.urls)),            # API under /api/
    path('register/', register_user, name='register_api'),  # API endpoint
    path('signup/', register_page, name='register_page'),
]
