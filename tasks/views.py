
from django.shortcuts import render
from rest_framework import viewsets, permissions 
from .models import Message, Task
from .serializers import MessageSerializer, TaskSerializer
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_username = self.request.query_params.get('user')
        if other_username:
            try:
                other_user = User.objects.get(username=other_username)
                return Message.objects.filter(
                    (models.Q(sender=user) & models.Q(receiver=other_user)) |
                    (models.Q(sender=other_user) & models.Q(receiver=user))
                )
            except User.DoesNotExist:
                return Message.objects.none()
        return Message.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_username = self.request.query_params.get('user')
        
        if other_username:
            try:
                other_user = User.objects.get(username=other_username)
            except User.DoesNotExist:
                return Task.objects.none()
            
            return Task.objects.filter(
                (models.Q(owner=user) & models.Q(shared_with=other_user)) |
                (models.Q(owner=other_user) & models.Q(shared_with=user))
            ).order_by('-priority', 'created_at')
        
        # Return the user's own tasks by default
        return Task.objects.filter(owner=user).order_by('-priority', 'created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

def frontend(request):
            return render(request, 'index.html')


def register_page(request):
    return render(request, 'register.html')  # This serves the HTML form

@csrf_exempt  # For development only – use CSRF tokens in production
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            User.objects.create_user(username=username, password=password)
            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
