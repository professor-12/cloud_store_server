from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User 
from .models import Profile , File ,  Folder



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
    



class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"



class FolderSerializer(ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"