from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

from django.db import transaction
from django.utils import timezone

from .models import Comment, ModelEvent, Post


BASE_TARGET_URL = "https://jsonplaceholder.typicode.com"


class NothingToSync(Exception):
    pass


@dataclass
class ModelSyncSettings:
    model: Comment | Post
    list_url: str


CommentSyncSettings = ModelSyncSettings(
    model=Comment,
    list_url=f"{BASE_TARGET_URL}/comments"
)

PostSyncSettings = ModelSyncSettings(
    model=Post,
    list_url=f"{BASE_TARGET_URL}/posts"
)

@dataclass
class SyncAction:
    db_table: str
    object_id: int
    event_type: ModelEvent.EventType

    __sync_settings_from_table_name = {
        Comment._meta.db_table: CommentSyncSettings,
        Post._meta.db_table: PostSyncSettings,
    }

    @property
    def sync_settings(self) -> ModelSyncSettings:
        return self.__sync_settings_from_table_name[self.db_table]
    
    @property
    def data(self) -> str | None:
        if self.event_type == ModelEvent.EventType.DELETED:
            return None
        model = self.sync_settings.model
        return model.objects.get(pk=self.object_id).to_sync_format()
    
    def perform(self):
        match self.event_type:
            case ModelEvent.EventType.CREATED:
                url = self.sync_settings.list_url
                print(f"POST {url} data='{self.data}'")
            case ModelEvent.EventType.UPDATED:
                url = f"{self.sync_settings.list_url}/{self.object_id}/"
                print(f"PUT {url} data='{self.data}'")
            case ModelEvent.EventType.DELETED:
                url = f"{self.sync_settings.list_url}/{self.object_id}/"
                print(f"DELETE {url}")


class SyncManager:
    actions = None
    model_events_qs = None
    model_events = None

    def _get_sync_actions(self) -> Iterator[SyncAction]:
        """Creates sync actions based on unsynced Model Events.

        It reduces amount of actions for each object to 1, by ignoring/removing
        redundant actions from Model Events log.
        """
        # Reduce amount of actions to only one for each object.
        main_actions = defaultdict(dict)
        for event in self.model_events:
            if event.entity_pk not in main_actions[event.entity_table]:
                # If this is the first appearance of action on this object -
                # save it.
                main_actions[event.entity_table][event.entity_pk] = event.type
            else:
                # If this is not the first appearance of action on this object -
                # compare it and leave only most important.
                prev_type = main_actions[event.entity_table][event.entity_pk]
                if (prev_type == ModelEvent.EventType.CREATED and 
                        event.type == ModelEvent.EventType.DELETED):
                    # Remove all events for this object because it was created
                    # and removed during one sync time frame.
                    del main_actions[event.entity_table][event.entity_pk]
                elif (prev_type == ModelEvent.EventType.UPDATED and 
                        event.type == ModelEvent.EventType.DELETED):
                    # Save only final deletion event.
                    main_actions[event.entity_table][
                        event.entity_pk
                    ] = event.type
                # Otherwise keep previous action in place as the main action.
        # Return selected events one by one with preserved order.
        for event in self.model_events:
            if main_actions[event.entity_table][event.entity_pk] == event.type:
                yield SyncAction(
                    db_table=event.entity_table,
                    object_id=event.entity_pk,
                    event_type=event.type
                )
                

    @transaction.atomic
    def start_periodical_sync(self):
        start_time = timezone.now()

        self.model_events_qs = ModelEvent.objects.unsynced()
        self.model_events = self.model_events_qs.all()
        if not self.model_events:
            raise NothingToSync()

        for action in self._get_sync_actions():
            action.perform()

        self.model_events_qs.update(synced_at=start_time)


