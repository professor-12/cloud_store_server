from django.urls import path
from .views import get , register , get_user  , profile , google , login

urlpatterns = [
      path('register/', register, name='register'),
      path("user/",get_user),
      path("profile/",profile),
      path("login/",login),
      path("google/callback/",google),
      path("seed/",get),
      # path("google/callback/",google)
]
