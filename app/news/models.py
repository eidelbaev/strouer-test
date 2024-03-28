"""Models"""
from django.db import models


class Post(models.Model):
    user_id = models.PositiveIntegerField()
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=1024)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    body = models.CharField(max_length=1024)
