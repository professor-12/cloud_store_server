from django.urls import path
from .views import *

urlpatterns = [
      path('register/', register, name='register'),
      path("login/",login,name="login"),
      path("createfolder/",createFolder),
      path("file/",createfile),
      path("user/",user),
      path("get-file/",getFiles),
      path("get-file/starred",getStarredFile),
      path("profile/",profile),
      # path("search/",searchFile),
      path("search/",searchFileVIEW.as_view()),
      path("spam/",spam),
]