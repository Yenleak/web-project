from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


# ─────────────────────────────────────────────
# Пользователь
# ─────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ["id", "name", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "name", "email"] 

        