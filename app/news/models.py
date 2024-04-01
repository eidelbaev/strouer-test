"""Models"""
import json

from django.db import models
    

class ModelEventQuerySet(models.QuerySet):
    """TODO Write docs"""

    def unsynced(self):
        """TODO Write docs"""
        return self.filter(synced_at__isnull=True)


class ModelEvent(models.Model):
    """TODO Write docs"""

    class EventType(models.TextChoices):
        CREATED = "CREATED"
        DELETED = "DELETED"
        UPDATED = "UPDATED"

    entity_table = models.CharField(max_length=128)
    entity_pk = models.PositiveIntegerField()
    type = models.CharField(max_length=16, choices=EventType.choices)
    logged_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(blank=True, null=True)

    objects = ModelEventQuerySet.as_manager()

    def __str__(self) -> str:
        return (
            f"ModelEvent(id={self.id}, entity_table={self.entity_table}, "
            "entity_pk={self.entity_pk}, type={self.type})"
        )


class TrackedModelMixin:
    """TODO Write docs"""

    def log_event(self, event_type: ModelEvent.EventType):
        print(f"{self} {event_type}")
        table_name = self._meta.db_table
        ModelEvent.objects.create(
            entity_table=table_name,
            entity_pk=self.id,
            type=event_type
        )

    def log_created(self):
        self.log_event(ModelEvent.EventType.CREATED)

    def log_deleted(self):
        self.log_event(ModelEvent.EventType.DELETED)

    def log_updated(self):
        self.log_event(ModelEvent.EventType.UPDATED)


class Post(models.Model, TrackedModelMixin):
    """TODO Write docs"""

    user_id = models.PositiveIntegerField()
    title = models.CharField(max_length=256)
    body = models.CharField(max_length=1024)

    def to_sync_format(self):
        return json.dumps({
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "body": self.body
        })

    def __str__(self) -> str:
        return f"Post(id={self.id})"

    class Meta:
        db_table = "news_post"


class Comment(models.Model, TrackedModelMixin):
    """TODO Write docs"""

    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    body = models.CharField(max_length=1024)

    def to_sync_format(self):
        return json.dumps({
            "id": self.id,
            "postId": self.post_id,
            "name": self.name,
            "email": self.email,
            "body": self.body
        })

    def __str__(self) -> str:
        return f"Comment(id={self.id}, post_id={self.post_id})"

    class Meta:
        db_table = "news_comment"
