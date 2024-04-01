# Reasoning while solving the task

## Table of Contents
1. [Requirements Analyzing](#requirements-analyzing)
2. [Start of Development](#start-of-development)
3. [Base Data Modeling](#base-data-modeling)
4. [Initial Data Importing](#initial-data-importing)
5. [CRUD API](#crud-api)
    - 5.1. [Issue with Primary Keys](#issue-with-primary-keys)
    - 5.2. [Authentication](#authentication)
6. [Synchronization](#synchronization)
    - 6.1. [Target API Limitations](#target-api-limitations)
    - 6.2. [Tracking the Changes](#tracking-the-changes)
    - 6.3. [Storing the Changes](#storing-the-changes)
    - 6.4. [Periodical Sync](#periodical-sync)
    - 6.5. [Full Sync](#full-sync)
7. [Testing & Linting](#testing-and-linting)


<a id="requirements-analyzing"></a>

## 1. Requirements Analyzing

Let's start with analyzing our requirements.

- Our application will be used only with Python 3, so we don't need to 
think of compatability with version 2;
- From the Django perspective we will be using: Django ORM for 
Database entries manipulation, Django migrations mechanism for 
keeping track and applying database schema changes (for not it will 
contain only initial migration) and Django commands for importing initial
data into database and performing synchronization;
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


<a id="start-of-development"></a>

## 2. Start of Development

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


<a id="base-data-modeling"></a>

## 3. Base Data Modeling

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


<a id="initial-data-importing"></a>

## 4. Initial Data Importing

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


<a id="crud-api"></a>

## 5. CRUD API

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


<a id="issue-with-primary-keys"></a>

### 5.1 Issue with Primary Keys

During testing POST /posts endpoint I found an issue: Imported by management
command objects didn't increment sequences for `post.id` and `comment.id` 
primary key fields. This is how objects creation in Django works using
PostgreSQL when we provide primary key values explicitly.

I came up with solution to manually update sequences to the right numbers 
after data import. I searched and found that this is a common solution
for this issue.


<a id="authentication"></a>

### 5.2 Authentication 

For authentication I used `djangorestframework-simplejwt` library which allows
us to work with JSON Web Tokens for authentication.


<a id="synchronization"></a>

## 6. Synchronization

As I understand from the task description and from the answer to my question,
I need to implement data synchronization mechanism from this Master system to
the Fake API Target system.

Here I see 2 ways of doing it: 
1. Dump all.
2. Apply only changes made since the last synchronization 
    (differential event-driven sync).

Syncing all data could be very time and memory expensive so it's not the optimal
way to achieve data synchronization in such project.
The other way is to perform periodical synchronization in small data chunks,
for example every 5 minutes or one hour.
It still does make sense to perform full sync once in a while, for example
every night (or any other time window when application is less used).

For the periodical sync we can log actions like Created, Updated, Deleted 
on our models and then merge them into Actions to be performed.
For example:
- if the Post was Created, then Updated - we will send only one "created"
    POST request to /posts endpoint;
- if the Post was Updated several times- we will send only one "updated"
    PUT request to /posts/{post_id} endpoint;
- if the Post was Updated, then Deleted- we will send only one "deleted"
    DELETE request to /posts/{post_id} endpoint;
- if the Post was Created, Updated and then Deleted - we will not
    send any requests;

It does make sense to log all actions and merge them later to provide a higher
throughput, not to perform any search in the logs table for each model update.

> For the demo purposes I'm not going to implement a scheduled (cron/celery)
> tasks. Sync commands will be just Django management commands supposed to be
> ran manualy. Output will be just a stdout messages from the commands.
> I think it's OK for this task.


<a id="target-api-limitations"></a>

### 6.1 Target API Limitations

Target API has explicit limitations and we have no control over its 
implimintations. We have no choice but to accept them and build our 
synchronisation with these constraints in mind.

Limitations:
- Bulk create/update operations is not possible
- Nested data is not supported
- Name of fields is not exactly how we want them to be in our system 
- etc...


<a id="tracking-the-changes"></a>

### 6.2 Tracking the Changes

I found that there are ready to use modules for tracking django model changes,
but it's an overkill for this case, we need just very basic features.
Looks like `Django Signals` mechanism is the right tool for tracking the changes
over our entities. 

For a more beatiful and dynamic implementation we could try to inherit our
models from an abstract model and track changes of abstract model, but for now
it's okay to register signals on each of our models separately. 

I've created `TrackedModelMixin` and Created/Updated/Deleted signals.
For some reason `post_save` signal is being triggered twice when object is being
created: first time with `created=True` (created) and second time with 
`created=False` (updated). I'll left it for the future, now it won't affect the
workflow since these actions will be merged into one action "Created" during
the synchronization process.


<a id="storing-the-changes"></a>

### 6.3 Storing the Changes

For simplicity we can use the same database and just create a new table for 
storing change log. For the more high performance solution we could use some
fast-to-write storage like NoSQL database, queue or messsage broker.

Change log table could be looking like this:

Model name: ModelEvent

|id |entity_table   |entity_pk |type   |logged_at          |synced_at          |
|---|---------------|----------|-------|-------------------|-------------------|
|1  |news_post      |10        |CREATED|2024-03-29 13:17:01|2024-03-29 13:20:00|
|2  |news_post      |10        |UPDATED|2024-03-29 13:18:46|2024-03-29 13:20:00|
|3  |news_comment   |53        |DELETED|2024-03-29 13:22:44|                   |
|4  |news_comment   |54        |CREATED|2024-03-29 13:23:15|                   |

I decided to store table name and not model name to make this data usable for
consumers which are not aware of our models (ORM) and could operate with our
database directly.

Do we need Syncs table storing synchronization jobs history?
Probably yes, but now we can keep it simple.


<a id="periodical-sync"></a>

### 6.4 Periodical Sync

It's very nice that Django handles deletion of dependant entities for us 
(by setting `on_delete=Models.CASCADE`) and sends signals for dependant entities
firts and then for "parent" entity. So we can just send these actions directly 
to the Target API and be sure that data will be deleted properly without causing
foreign key constraint violation (when we try to delete Post first).
We don't have control over the Target API implementation and since it's a fake
API, we can't actually check whether deleting Post will cause CASCADE deleting
of its Comments or not. So as a fail-safe measure we will delete comments first.

As I explained earlier in the beginning of this section 
[(6. Synchronization)](#synchronization), I'm going to "merge" several actions
executed over single object into just one action that should be performed on 
Target API in order to have data up-to-date (sometimes even no actions will
be needed e.g. when object was created and deleted during one synchronization
time frame). 

I'n order not to be blocked by the Target API we need to comply the normal 
rate-limit and not to attack it with hundreds requests per second.
But I'll keep it out of the scope of this task.

Also for simplicity I assume that connection will never be lost and each
synchronization will finish successfully. Otherwise we will need to mark each
ModelEvent entry whether it was successfully synced or not, since we don't have
a transaction mechanism on top of our integration with the Target API and each
event could be successfully sent or not independently of other event.

One more thing that I did for simplicity was that I load `SyncAction.data` from
affected objects one-by-one during execution and not load them all together
beforehand (knowing their ids). It's not cool because we create redundant load
for our database, but it was just easier to implement in timely manner.
I had a prototype with loading all affected objects from database in once, but
decided to simplify the code in this case.


<a id="full-sync"></a>

### 6.5 Full Sync

Full sync I didn't implement, due to limited time. It's also quite tricky,
because we can't just send all data in our database to Target API and say
"replace everything with this data". We need to "check" what's already in
Target API, what's not, find differences, eliminate them.
Then it's already not a Full Sync but a different version of differencial
sync.


<a id="testing-and-linting"></a>

## 7. Testing & Linting

Automated testing is always an integral part of development for me. 
Unfortunately, in this case the test task took longer than I had planned and 
I can no longer devote more time to writing tests. 

What would I cover in the first place?
I would start with the most high-level tests such as testing API endpoints 
and "import initial data" and "Periodical sync" commands. After this we could
go deeper in integration and unit tests.

Usually I also implement auto linters checks in Makefile or python invoke 
commands, or even on github pre-commit hooks. 
Recently I moved from pylint, flake8 and bunch of other linters and plugins to
`ruff` and was very happy about it. If I had more time I'd definitelly implement
this check here, but I think it's not a must.
