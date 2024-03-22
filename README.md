### Initial run

In order to build our application and apply initial migrations
we need to run the following commands:

```bash
docker compose up -d --build
```

```bash
docker compose exec web python manage.py migrate --noinput
```