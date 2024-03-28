## Initial run

In order to build our application and apply initial migrations
we need to run the following commands:

```bash
docker compose up -d --build
```

```bash
docker compose exec web python manage.py migrate --noinput
```

Let's create a superuser (very bad idea to have credentials here,
but it's just for the demo purposes):
```bash
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=admin
docker compose exec web python manage.py createsuperuser --noinput
```

## Using the application

### Run the application

...

### Authentication

```bash
curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json; indent=2" \
    -d '{"username": "admin", "password": "admin"}' \
    http://localhost:8000/api-auth/token/
```

Example output:
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNTUzNTkyLCJpYXQiOjE3MTE1NTMyOTIsImp0aSI6ImU4ZDhmZGViYzRiMjQ2NDg5MmJhZGRlM2M0MDI1MjRiIiwidXNlcl9pZCI6MX0.dTkGn-1wsGwbTNHsYywLmMVwEBHboRAVTDlkXf7hNPI",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMTYzOTY5MiwiaWF0IjoxNzExNTUzMjkyLCJqdGkiOiI0MjE5NmQ2NjZmNWM0ZWI5YWI1MDIzMmNmODJhM2E5NiIsInVzZXJfaWQiOjF9.NYNKcGlIKOYhv06yTAqZfOKtR7raxbnzoOKqU968Ots"
}
```

Copy the access token and create an environment variable holding this value:
```bash
export DJANGO_ACCESS_TOKEN=your_access_token_here
```
This env variable will be used in the following examples.
Generated token will be valid for 1 hour, after that please generate new one.
I didn't put here refershing URL just for simplicity.

### Making queries

Assuming that we've ran our application, applied migrations, imported data,
authenticated and exported auth token to the environment, we now can make 
some queries to test out our API.

```bash
curl \
    -X GET \
    -H "Accept: application/json; indent=2" \
    -H "Authorization: Bearer ${DJANGO_ACCESS_TOKEN}" \
    http://localhost:8000/news/posts/
```

Example output (10 most recent posts):
```json
{
  "count": 100,
  "next": "http://localhost:8000/news/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 100,
      "title": "at nam consequatur ea labore ea harum",
      "body": "cupiditate quo est a modi nesciunt soluta\nipsa voluptas error itaque dicta in\nautem qui minus magnam et distinctio eum\naccusamus ratione error aut"
    },
    {
      "id": 99,
      "title": "temporibus sit alias delectus eligendi possimus magni",
      "body": "quo deleniti praesentium dicta non quod\naut est molestias\nmolestias et officia quis nihil\nitaque dolorem quia"
    },
    ...
  ]
}
```