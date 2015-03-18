#! /bin/bash

/home/igor/.virtualenvs/vkrsys/bin/gunicorn -c /home/igor/Projects/python/vkrsys/gunicorn.conf vkrsys.wsgi:application