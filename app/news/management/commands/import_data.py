"""Initial data import command."""
from datetime import datetime
from itertools import islice
from typing import Any, Literal
import requests

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from news.models import Post, Comment


type Resource = Literal["posts", "comments"]
BASE_URL = "https://jsonplaceholder.typicode.com"


def check_that_tables_are_empty() -> bool:
    """Returns True if Post and Comment tables are empty and we can proceed."""
    return not (Post.objects.exists() or Comment.objects.exists())


def get_list_of_entries(resource: Resource) -> list[dict]:
    """Fetch the data from Fake API, scheck, parse and return it."""
    res = requests.get(f"{BASE_URL}/{resource}", timeout=10)
    res.raise_for_status() 
    return res.json()

def update_db_sequences() -> None:
    """Set current values of PK sequences accordingly to the data we have."""
    max_post_id = Post.objects.latest('id').id
    max_comment_id = Comment.objects.latest('id').id

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval('news_post_id_seq', %s);", [max_post_id]
            )
        cursor.execute(
            "SELECT setval('news_comment_id_seq', %s);", [max_comment_id]
            )

class Command(BaseCommand):
    help = "Import initial Posts and Comments data into database."

    def handle(self, *args: Any, **options: Any) -> str | None:
        start = datetime.now()
        start_str = start.strftime("%m/%d/%Y, %H:%M:%S")
        self.stdout.write(f"{start_str}: Import started")

        if not check_that_tables_are_empty():
            end_str = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            self.stdout.write(
                self.style.ERROR(
                    f"{end_str}: Target tables are not empty, can't proceed."
                )
            )
            return
        
        posts = get_list_of_entries("posts")
        comments = get_list_of_entries("comments")

        new_posts = (
            Post(
                id=post["id"],
                user_id=post["userId"],
                title=post["title"],
                body=post["body"],
            ) for post in posts
        )
        new_comments = (
            Comment(
                id=comment["id"],
                post_id=comment["postId"],
                name=comment["name"],
                email=comment["email"],
                body=comment["body"],
            ) for comment in comments
        )

        with transaction.atomic():
            batch_size = 100
            # Create all posts in batches of 100
            while True:
                batch = list(islice(new_posts, batch_size))
                if not batch:
                    break
                Post.objects.bulk_create(batch, batch_size)

            # Create all comments in batches of 100
            while True:
                batch = list(islice(new_comments, batch_size))
                if not batch:
                    break
                Comment.objects.bulk_create(batch, batch_size)

        # At this point our data has been already imorted and we need to
        # update postgresql sequences for primary keys, because it doesn't
        # happen automatically when we specify primary key explicitly.
        update_db_sequences()

        end = datetime.now()
        end_str = end.strftime("%m/%d/%Y, %H:%M:%S")
        elapsed_sec = (end - start).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(
                f"{end_str}: Imported {len(posts)} posts "
                f"and {len(comments)} comments, "
                f"elapsed time: {elapsed_sec:.2f}s."
            )
        )
