from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Folder(models.Model):
    name = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    star = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parentFolder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "user"], name="unique_folder_per_user")
        ]

    def __str__(self):
        return f'{self.name} (Owned by {self.user.username})'


class File(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=100)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    file = models.FileField(upload_to="files/%Y/%m/%d/")
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    star = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    spam = models.BooleanField(default=False)
    isTempDeleted = models.BooleanField(default=False)
    

    class Meta:
        verbose_name_plural = "Files"

    def __str__(self):
        return f'{self.name}'
