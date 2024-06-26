Create a simple REST API to interact with the Fake API in [JSONPlaceholder - Free Fake REST API](https://jsonplaceholder.typicode.com/)

1. Create a Django command to import the data for the first time (posts and comments only) from [JsonPlaceholder Free Fake Rest API](https://jsonplaceholder.typicode.com/) to the local Postgres.
   - You cannot modify the external provider data structure.
   - You can define whatever you want in your local database.
2. Create a Rest API to manage that data in those models.
3. Implement all CRUD operations.
   - The user_id for the new posts created is always 99999942 since we don’t implement the user model.
   - Provide users authentication and request authorization through Bearer Token.
4. Synchronize both systems. The system you are implementing is the MASTER. You can decide how and when this synchronization will be done. Please write a README to specify how it can be triggered.
5. We prefer a tested and well documented task than a quick one.

Technical Requirements:
- Use Python 3
- Use Django with Django REST framework.
- Use PostgreSQL
- Deliver the task using Docker and docker-compose.

Notes:
You can resort to use any library that you need but specify the purpose of including it.

