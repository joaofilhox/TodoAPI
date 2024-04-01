from rest_framework import serializers
from accounts.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}
    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)    

class LoginSerializer(serializers.Serializer):
        username = serializers.CharField(max_length=150)
        password = serializers.CharField(max_length=128)
