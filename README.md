vkrsys
====

### Songs recommendation system.
Based on [rsys](https://github.com/igorcoding/rsys) library.

There are two main things in this project:

1. The actual frontend application written in Django
2. Backend package (```recommender_api```) written using Tornado server and rsys library

To start everything you need to start three servers:

1. ```python manage.py runserver 0.0.0.0 8000```
2. ```celery -A vkrsys worker -l debug```
3. ```python recommender_api/server.py```
