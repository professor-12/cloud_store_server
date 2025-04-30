from rest_framework.serializers import ModelSerializer
from .models import *
from django.contrib.auth.models import User



class ProfileSerializer(ModelSerializer):
      class Meta:
            fields = "__all__"
            model =  Profile

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    