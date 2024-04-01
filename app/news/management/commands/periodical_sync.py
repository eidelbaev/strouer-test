"""Periodical sync command."""
from datetime import datetime
from typing import Any

from django.core.management.base import BaseCommand

from news.sync import SyncManager, NothingToSync


class Command(BaseCommand):
    help = "Sync unsynced data."

    def handle(self, *args: Any, **options: Any) -> str | None:
        start = datetime.now()
        start_str = start.strftime("%m/%d/%Y, %H:%M:%S")
        self.stdout.write(f"{start_str}: Sync started")

        try:
            sync_manager = SyncManager()
            sync_manager.start_periodical_sync()

            end = datetime.now()
            end_str = end.strftime("%m/%d/%Y, %H:%M:%S")
            elapsed_sec = (end - start).total_seconds()
            self.stdout.write(
                self.style.SUCCESS(
                    f"{end_str}: Sycsessfully synced, "
                    f"elapsed time: {elapsed_sec:.2f}s."
                )
            )
        except NothingToSync:
            end_str = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            self.stdout.write(
                self.style.WARNING(f"{end_str}: Nothing to sync.")
            )
