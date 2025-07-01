from urllib import request
from django.shortcuts import render
from rest_framework import viewsets, permissions 
from .models import Message, Task
from .serializers import MessageSerializer, TaskSerializer
from django.contrib.auth.models import User
from django.db import models
import cv2
import os
import numpy as np
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.conf import settings
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

