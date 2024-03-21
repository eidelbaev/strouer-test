Let's start with analyzing our requirements.

- Our application will be used only with Python 3, so we don't need to 
think of compatability with version 2;
- From the Django perspective we will be using: Django ORM for 
Database entries manipulation, Django migrations mechanism for 
keeping track and applying database schema changes (for not it will 
contain only initial migration) and Django commands for importing initial
data into database and performing testing and linting jobs;
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

