from rest_framework import permissions, viewsets
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin,
    UpdateModelMixin
)

from .models import Comment, Post
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Posts to be viewed or edited.
    """
    queryset = Post.objects.all().order_by("-id")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    
    def perform_create(self, serializer):
        # predefined user_id value that we agreed to use
        serializer.save(user_id=99999942)
        return super().perform_create(serializer)


class CommentViewSet(
        viewsets.GenericViewSet,
        RetrieveModelMixin,
        UpdateModelMixin,
        DestroyModelMixin
    ):
    """
    API endpoint that allows Comments to be viewed or edited.
    """
    queryset = Comment.objects.all().order_by("-id")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer


class CommentsInPostViewSet(
        viewsets.GenericViewSet,
        CreateModelMixin,
        ListModelMixin
    ):
    """
    API endpoint that allows Comments to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post_id=post_id).order_by("-id")
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        serializer.save(post_id=post_id)
        return super().perform_create(serializer)
