"""Models"""
from django.db import models


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveIntegerField()
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=1024)


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    body = models.CharField(max_length=1024)
