from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes , authentication_classes , parser_classes
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser , FormParser
from .serializers import FolderSerializer, UserSerializer , ProfileSerializer , FileSerializer
from django.contrib.auth.models import User 
from .models import Folder , File , Profile
from rest_framework.permissions import IsAuthenticated
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics , filters 

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # Validate input fields
    if not username or not password or not email:
        return Response({'error': 'Username, email, and password are required.'}, status=400)

    # Check if the email or username already exists
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email is already registered.'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username is already taken.'}, status=400)

    #  Create a profile

    # Create a drive

    # Serialize and save user data
    user_serializer = UserSerializer(data={'username': username, 'password': password, 'email': email})

    if user_serializer.is_valid():
        user = user_serializer.save()
        # Set and hash the password
        user.set_password(password)
        user.save()
        name="C_DRIVE"+"_" + username + str(user.id)
        folder = Folder.objects.create(name=name,user=user)

        folder.save()
        folderSeializer = FolderSerializer(folder)

        user_profile = ProfileSerializer(data={'user':user.id})

        if user_profile.is_valid():
            user_profile.save()

        # Create an authentication token
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': user_serializer.data,
            'token': token.key,
            'profile': user_profile.data,
            'drive': folderSeializer.data
        }, status=201)

    # Return validation errors
    return Response(user_serializer.errors, status=400)


@api_view(["POST"])
def login(request, *args, **kwargs):
    email = request.data.get("email")
    password = request.data.get("password")

    # Validate input
    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=400)

    try:
        # Retrieve user by email
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials."}, status=401)

    # Check password validity
    if not user.check_password(password):
        return Response({"error": "Invalid credentials."}, status=401)

    # Serialize user data and create token
    user_data = UserSerializer(user).data
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'user': user_data,
        'token': token.key
    }, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([TokenAuthentication])  # Use token authentication
def createFolder(request):
    name = request.data.get("name")
    # Validate folder name input
    if not name:
        return Response({"error": "Folder name is required."}, status=400)

    # Check if the folder name already exists for the user
    if Folder.objects.filter(name=name, user=request.user).exists():
        return Response({"error": "Folder with this name already exists."}, status=400)

    # Create the folder associated with the authenticated user
    folder = Folder.objects.create(name=name, user=request.user)

    return Response({
        "message": "Folder created successfully.",
        "folder": {
            "id": folder.id,
            "name": folder.name,
            "user": folder.user.username
        }
    }, status=201)


@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createfile(request):
    if not request.data.get('folder'):
        request.data['folder'] = Folder.objects.get(name="C_DRIVE"+ "_" + request.user.username + str(request.user.id)).id
        print(request.data)
    request.data['user'] = request.user.id
    file_serializer = FileSerializer(data=request.data)
    if file_serializer.is_valid(raise_exception=True):
        file_serializer.save()
        print(file_serializer.data)
        return Response("Created",status=200)
    return Response("Created",status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user(request):
    userSerializer = UserSerializer(request.user)
    return Response({ "user": userSerializer.data },status=200)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getFiles(request):
    files = File.objects.filter(user=request.user)
    fileSerializer = FileSerializer(files,many=True)
    return Response({ "files": fileSerializer.data },status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getStarredFile(request):
    starred_file = File.objects.filter(user=request.user,star=True)
    json = FileSerializer(starred_file,many=True)
    return Response(json.data,status=200)



@api_view(['GET','POST'])
@parser_classes([MultiPartParser,FormParser])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    profile = Profile.objects.get(user=request.user.id)
    if request.method == "GET":
        profiledata = ProfileSerializer(profile)

        return Response(profiledata.data)
    elif request.method == "POST":
        profileSerializer  = ProfileSerializer(profile,data=request.data,partial=True)
        if profileSerializer.is_valid(raise_exception=True):
            profileSerializer.save()
            return Response(profileSerializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def searchFile(request):
    query = request.GET.get("search", "").strip()  
    print(query)
    if not query:  
        return Response([], status=200)


    files = File.objects.filter(user=request.user,name__icontains=query).distinct()


    # Serialize the filtered files
    json_file = FileSerializer(files, many=True)

    return Response(json_file.data, status=200)


class searchFileVIEW(generics.ListAPIView):
    queryset = File.objects.filter
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# @api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def search(request):
#     queryset = File.objects.filter(user=request.user,name__icontain=request.GET.get("search"))



@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def spam(request):
    spam_file = File.objects.filter(user=request.user,spam=True)
    _json = FileSerializer(spam_file,many=True)
    return Response(_json.data,status=200)