from django.urls import path
from .views import *

urlpatterns = [
      path("createfolder/",createFolder),
      path("file/",createfile),
      path("get-file/",getFiles),
      path("get-file/starred",getStarredFile),
      path("search/",searchFile),
      path("spam/",spam),
      path("delete-file/",deleteFile)
]