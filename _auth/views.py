import cloudinary.uploader
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from core.models import Profile as OldProfile
from core.serializers import ProfileSerializer
from .models import Profile as NewProfile
from .serializers import ProfileSerializer  as NewProfileSerializer
from core.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes  , authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated 
import requests
import os
import cloudinary
from core.utlils import uploadImage

@api_view(["GET"])      
def get(request):
      allOldProfile = OldProfile.objects.all()
      _data = ProfileSerializer(allOldProfile,many=True)
      print(_data.data)
      for i in _data.data:
            data = {
        "bio": i.get('bio'),
        "location": i.get("location"),
        "birth_date": i.get("birth_date"),
        "profile_picture": i.get("profile_picture") or "",
        "created_at": i.get("created_at"),
        "updated_at": i.get("updated_at"),
        "user": i.get("user")
        }
            profile = NewProfileSerializer(data=data)
            if profile.is_valid():
                  profile.save()
                  print(profile.data)
      
      return Response(_data.data,status=200)


@api_view(['GET','POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    profile = NewProfile.objects.get(user=request.user.id)
    if request.method == "GET":
        profiledata = NewProfileSerializer(profile)
        return Response(profiledata.data)
    
    elif request.method == "POST":
        profilePicture = request.data.get("profile_picture")
        if profilePicture is not None:
            _cloudinary = uploadImage(profilePicture)
            if _cloudinary:
                request.data["profile_picture"] = _cloudinary
            else:
                return Response({"message":"Unable to upload image"},status=400)
        profileSerializer  = NewProfileSerializer(profile,data=request.data,partial=True)
        if profileSerializer.is_valid(raise_exception=True):
            profileSerializer.save()
            return Response(profileSerializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    userSerializer = UserSerializer(request.user)
    return Response({ "user": userSerializer.data },status=200)



@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    
    if not username or not password or not email:
        return Response({'error': 'Username, email, and password are required.'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered.'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken.'}, status=400)

    user_serializer = UserSerializer(data={'username': username, 'password': password, 'email': email})

    if user_serializer.is_valid():
        user = user_serializer.save()
        user.set_password(password)
        user.save()
        name="C_DRIVE"+"_" + username + str(user.id)
        folder = Folder.objects.create(name=name,user=user)
        folder.save()
        user_profile = ProfileSerializer(data={'user':user.id})
        if user_profile.is_valid():
            user_profile.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': user_serializer.data,
            'token': token.key,
            'profile': user_profile.data,
        }, status=201)
    return Response(user_serializer.errors, status=400)


@api_view(["POST"])
def login(request, *args, **kwargs):
    email = request.data.get("email")
    password = request.data.get("password")

    # Validate input
    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials."}, status=401)
    
    if not user.check_password(password):
        return Response({"error": "Invalid credentials."}, status=401)

    # Serialize user data and create token
    user_data = UserSerializer(user).data
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'user': user_data,
        'token': token.key
    }, status=200)




@api_view(["GET"])
def google(request):
    code = request.GET.get("code")
    if code is None:
       return Response({"message": "No code provided"}, status=400)

    PARAMS = {
        "client_id": os.environ.get("google_id") or "",
        "client_secret": os.environ.get("google_secret"),
        "redirect_uri": os.environ.get("redirect_uri"),
        "code": code,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post("https://oauth2.googleapis.com/token", data=PARAMS, headers=headers)

    if token_response.status_code != 200:
        print(token_response.json())
        return Response({"message": "Failed to get access token", "error": token_response.json()}, status=400)

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if user_info_response.status_code != 200:
        return Response({"message": "Failed to fetch user info"}, status=400)

    user_info = user_info_response.json()
    existing_user = User.objects.filter(email=user_info["email"]).first()

    if existing_user:
        token, created = Token.objects.get_or_create(user=existing_user)
        user_data = UserSerializer(existing_user).data
        return Response({
            'user': user_data,
            'token': token.key
        }, status=200)

    # Creating a new user
    create_user = SocialUserSerializer(data={"email": user_info["email"], "username": user_info["given_name"]})

    if create_user.is_valid():
        user_instance = create_user.save()
        token, created = Token.objects.get_or_create(user=user_instance)
        profile = NewProfileSerializer(data={"user": user_instance.id, "proflle_picture":user_info["picture"]},partial=True)
        if profile.is_valid():
            profile.save()
        return Response({
            'user': create_user.data,
            'token': token.key
        }, status=200)

    return Response({"message":"An error occured, Pleasee try again later"},status=500)
