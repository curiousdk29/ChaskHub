from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth.models import User
from .models import Message,Task

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class MessageSerializer(serializers.ModelSerializer):


    sender = serializers.StringRelatedField(read_only=True)
    receiver = serializers.CharField()  # Accept username as string

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

    def create(self, validated_data):
        receiver_username = validated_data.pop('receiver')
        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"receiver": "User not found."})

        sender = self.context['request'].user
        return Message.objects.create(sender=sender, receiver=receiver, **validated_data)






class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    shared_with = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required=False # Add this if sharing is optional
    )

    class Meta:
        model = Task
        fields = ['id', 'owner', 'shared_with', 'title', 'description', 'priority', 'completed', 'created_at']
        # Also, make 'owner' read-only in Meta to prevent it from being in validated_data from user input
        read_only_fields = ['owner'] # Ensure owner is not expected in incoming data

    def create(self, validated_data):
        # Pop the shared_with field which contains a list of User objects
        # Use .pop with a default empty list to avoid KeyError if 'shared_with' is missing
        shared_with_users = validated_data.pop('shared_with', [])

        # The 'owner' is already in validated_data because of serializer.save(owner=...)
        # So, simply pass **validated_data to create the Task instance
        task = Task.objects.create(**validated_data) # <--- FIX IS HERE

        # Set the ManyToMany relationship after the task is created
        if shared_with_users:
            task.shared_with.set(shared_with_users)
            
        return task

