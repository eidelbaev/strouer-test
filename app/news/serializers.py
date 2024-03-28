from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post_id", "name", "email", "body"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "user_id", "title", "body"]
        read_only_fields = ["user_id"]
