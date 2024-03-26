"""Initial data import command."""
from collections import defaultdict
from datetime import datetime
from typing import Any, Literal
import requests

from django.core.management.base import BaseCommand
from django.db import transaction

from news.models import Post, Comment


type Resource = Literal["posts", "comments"]
BASE_URL = "https://jsonplaceholder.typicode.com"


def get_list_of_entries(resource: Resource) -> list[dict]:
    """Fetch the data from Fake API, scheck, parse and return it."""
    res = requests.get(f"{BASE_URL}/{resource}", timeout=10)
    res.raise_for_status() 
    return res.json()


def map_comments_to_post_id(comments: list[dict]) -> dict[int, list[dict]]:
    """Create dict with post_id as a key and list of comments as a value."""
    result = defaultdict(list)
    for comment in comments:
        result[comment["postId"]].append(comment)
    return result

class Command(BaseCommand):
    help = "Import initial Posts and Comments data into database."

    def handle(self, *args: Any, **options: Any) -> str | None:
        start = datetime.now()
        start_str = start.strftime("%m/%d/%Y, %H:%M:%S")
        self.stdout.write(f"{start_str}: Import started")
        
        posts = get_list_of_entries("posts")
        comments = get_list_of_entries("comments")

        comments_for_post_id = map_comments_to_post_id(comments)

        with transaction.atomic():
            for post in posts:
                new_post = Post.objects.create(
                    id=post["id"],
                    user_id=post["userId"],
                    title=post["title"],
                    body=post["body"],
                )
                for comment in comments_for_post_id[new_post.id]:
                    Comment.objects.create(
                        id=comment["id"],
                        post=new_post,
                        name=comment["name"],
                        email=comment["email"],
                        body=comment["body"],
                    )

        end = datetime.now()
        end_str = end.strftime("%m/%d/%Y, %H:%M:%S")
        elapsed_sec = (end - start).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(
                f"{end_str}: Imported {len(posts)} posts and {len(comments)} comments, "
                f"elapsed time: {elapsed_sec:.2f}s."
            )
        )
