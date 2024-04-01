from rest_framework import serializers
from .models import Task  

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['created_at', 'updated_at', 'owner']  # Certifique-se de incluir 'owner' em read_only_fields também