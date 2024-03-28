### 1. Requirements amalyzing 

Let's start with analyzing our requirements.

- Our application will be used only with Python 3, so we don't need to 
think of compatability with version 2;
- From the Django perspective we will be using: Django ORM for 
Database entries manipulation, Django migrations mechanism for 
keeping track and applying database schema changes (for not it will 
contain only initial migration) and Django commands for importing initial
data into database and performing testing and linting jobs;
- We don't need to use Django Admin, static and media files, django views
and django templates;
- For REST API endpoints and authentication we will be using Django REST 
Framework;
- As the main database we will be using PostgreSQL;
- As for the delivering the project, we need to dockerize the application 
and put all requirements into docker-compose file for simple local setup.

Since this is a green field application, I'm going to use the freshest LTS
(where applicable) versions of the software:
- Python 3.12
- Django 4.2
- Django REST Framework 3.15 (starts supporting Python 3.12)
- PostgreSQL 16 
- Psycopg 2.9.9 (starts supporting Python 3.12)

### 2. Start of development

I created an initial Django application using `django-admin` command.

Then I wrapped it alongsite with `requirements.txt` into Docker container 
and created `docker-compose.yml` file for easy local deployment.

I chose to keep using built-in development web server that Django comes
with, because it's enough for the purposes of this task. 
For production deployemnt we should replace it with more advanced and 
powerfull app web server like `gunicorn` (WSGI) or `uvicorn` (ASGI),
plus place it behind some reverse proxy like `nginx` to allow application
server do only its direct tasks and leave low-level networking, caching
and access control on a high-performance web server.

### 3. Base Data Modeling

Let's take a look at the data we are going to work with.
We need to perform CRUD operations over two entities: Post and Comment.
Author (or User) model is redundant for this task - `user_id` for loaded 
from Fake API Posts will remain simple integer value, for the new Posts
it will always be a constant value of `99999942`.

At the first glance, we need to create the following Models and fields:

- Post
    - `id`: int, primary key
    - `user_id`: int
    - `title`: str, max length = 256
    - `body`: str, max length = 1024 (let's say, short Posts only)

- Comment
    - `id`: int, primary key
    - `post_id`: int, foreigh key to Post
    - `name`: str, max length = 128
    - `email`: str, max length = 128
    - `body`: str, max length = 1024 (let's say, short Posts only)

Notes:
 - `body` fields will have CharField class instead of TextField, becuse
    TextField is too big for our purposes (65,535 bytes max) and can't
    be limited to lower size, except of 255 bytes which is too low.
- I used snake_case naming convention instead of camelCase used in
    Fake API for better alighnment with the Python standards.

During working on the Synchronization topic we could further extend 
our models and even create new ones.

### 4. Initial data import

In order to import initial data in our system from Fake API we need to use
Django command.

Since this command is intended to be used only once for an initial data
import, I propose that in order to execute the command, several conditions 
must be met: 
- Tables for `Posts` and `Comments` must be empty;
- Increment values for `id`s must be reset to 0, so that we can insert
    imported posts with their real ids and the next post created on our 
    system will get the incremented value from the imported post and
    not from the previously created posts (on our system, during tests).

Since our application is synchronous, I'm going to use `requests` library
for fetching data from the Fake API. In case we were developing async
application, I would choose `httpx` or `aiohttp` client.

I intentionally didn't implement any exceptions handling in this command,
bacause it brings only unnececessary complexity to the code. This is a
internal command that should be used only once, so it's okay to receive
an unhandled exception.

### 5. CRUD API

I want to start with implementing CRUD API first, without implementing any
synchronization-related measures. Since this application will be "released"
only with synchronization in place, it's totally fine to have something
slightly rebuilt/redesigned during the development.

**Actions that our API should support:**

Post:
- Get list of Posts (paginated and all)
- Create single Post
- Get single Post
- Update single Post (full update, not partial)
- Delete single Post

Comments:
- Get list of Comments for exact Post (paginated and all)
- Create new Comment for exact Post
- Get single Comment
- Update single Comment (full update, not partial)
- Delete single Comment

**Endpoints that should be implemented:**

Posts:
- `GET /posts/` - Get list of Posts
- `POST /posts/` - Create single Post
- `GET /posts/{post_id}/` - Get single Post
- `PUT /posts/{post_id}/` - Update single Post
- `DELETE /posts/{post_id}/` - Delete single Post

Comments:
- `GET /comments/{comment_id}/` - Get single Comment
- `PUT /comments/{comment_id}/` - Update single Comment
- `DELETE /comments/{comment_id}/` - Delete single Comment

Nested endpoints:
- `GET /posts/{post_id}/comments/` - Get list of Comments for exact Post
- `POST /posts/{post_id}/comments/` - Create single Comment for exact Post

* Note that these endpoints will be located after application's base 
namespace `/news/`. For example `/posts/` will be accesable via
`localhost:8000/news/posts/`.

For simplicity I used ModelViewSet and GenericViewSet with Mixins.
For the same reason I decided not to implement nested views such as 
Comments list in Post.

#### 5.1 Issue with primary keys

During testing POST /posts endpoint I found an issue: Imported by management
command objects didn't increment sequences for `post.id` and `comment.id` 
primary key fields. This is how objects creation in Django works using
PostgreSQL when we provide primary key values explicitly.

I came up with solution to manually update sequences to the right numbers 
after data import. I searched and found that this is a common solution
for this issue.

#### 5.2 Authentication 

for authentication I used `djangorestframework-simplejwt` library which allows
us to work with JSON Web Tokens for authentication.

### 6. Synchronization

As I understand from the task description and from the answer to my question,
I need to implement data synchronization mechanism from this Master system to
the Fake API Target system.

Here I see 2 ways of doing it: 
1. Dump all.
2. Apply only changes made since the last synchronization 
    (differential event-driven sync).

< Elaborate on the second option, why it's better and how I want to
implement it... >

We can log actions like Created, Updated, Deleted on our models
and then merge them into Actions to be performed.
For example:
- if the Post was Created, then Updated - we will send only one
    POST request to /posts endpoint;
- if the Post was Created, Updated and them Deleted - we will not
    send any requests;

< This chapter will continue to be updated ... >


<!-- TODO Some notes:

1. For the initial import of posts and comments and for further sync
we need to implement a Fake API service abstraction that will handle it.

Limitadions of Fake API:
- no filtration: batch processing is not possible, only "load all"
- I assume that POST method on /posts and /posts/{id}/comments endpoints 
    expects only single entry. That means we need to create Posts and Comments
    one-by-one.
- I assume, that 
- Since our target system is available only via simple REST API, we cannot



 -->