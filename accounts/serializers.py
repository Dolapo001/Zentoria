from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'fullname', 'password', 'gender', 'profile_picture', 'address', 'phone_number',
                  'birthday')
        extra_kwargs = {
            'password': {'write_only': True}
        }
