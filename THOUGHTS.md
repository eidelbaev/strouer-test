### Requirements amalyzing 

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

### Start of development

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

### Base Data Modeling

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

*`body` fields will have CharField class instead of TextField, becuse
TextField is too big for our purposes (65,535 bytes max) and can't
be limited to lower size, except of 255 bytes which is too low.

During working on the Synchronization topic we could further extend 
our models and even create new ones.

### Synchronization

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