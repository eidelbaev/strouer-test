from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"posts", views.PostViewSet)
router.register(r"comments", views.CommentViewSet)

comments_in_post = views.CommentsInPostViewSet.as_view({
    "get": "list",
    "post": "create"
})

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<int:post_id>/comments/",
        comments_in_post,
        name="comments-in-post"
    )
]
