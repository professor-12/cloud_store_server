from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes , authentication_classes , parser_classes
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser , FormParser
from .serializers import *
from django.contrib.auth.models import User 
from .models import Folder , File , Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics , filters 
import os
import requests
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication]) 
def createFolder(request):
    name = request.data.get("name")
    # Validate folder name input
    if not name:
        return Response({"error": "Folder name is required."}, status=400)

    # Check if the folder name already exists for the user
    if Folder.objects.filter(name=name, user=request.user).exists():
        return Response({"error": "Folder with this name already exists."}, status=400)

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
    request.data['user'] = request.user.id
    try:
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid(raise_exception=True):
            file_serializer.save()
            print(file_serializer.data)
            return Response("Created",status=200)
        return Response("Created",status=200)
    except:
        return Response({"message":"Connection error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteFile(request):
    print(request.data)
    file = File.objects.get(user=request.user,id=request.data["id"])
    if file:
        file.delete()
        return Response({"message":"File deleted successfully"},status=status.HTTP_200_OK)
    return Response({"message":"File not found"},status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getFiles(request):
    files = File.objects.filter(user=request.user).order_by("-created_at")
    fileSerializer = FileSerializer(files,many=True)
    return Response({ "files": fileSerializer.data },status=200)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def renameFiles(request):
    
    pass



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getStarredFile(request):
    starred_file = File.objects.filter(user=request.user,star=True)
    json = FileSerializer(starred_file,many=True)
    return Response(json.data,status=200)




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



@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def spam(request):
    spam_file = File.objects.filter(user=request.user,spam=True)
    _json = FileSerializer(spam_file,many=True)
    return Response(_json.data,status=200)



