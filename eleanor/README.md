

**eleanor**:

Demo and code I use to go along my talk on patterns for building resilient applications on AWS. 


To Get started - in one terminal run:

> docker-compose up 


In another:

> docker-compose run eleanor-api python3 create_db.py



then you can create users:

➜  ~ http get http://127.0.0.1:80/api/user/77c059e7a4d740ed9416e285c8d57b04
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 126
Content-Type: application/json
Date: Fri, 22 Feb 2019 12:18:30 GMT
Server: gunicorn/19.9.0

{
    "id": "77c059e7a4d740ed9416e285c8d57b04",
    "phone": "+358456315",
    "timestamp": "2019-02-22 12:11:04.000",
    "username": "user1"
}

and see the screen logs that it is using master

The you can fetch user1

➜  ~ http get http://127.0.0.1:80/api/user/77c059e7a4d740ed9416e285c8d57b04
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 126
Content-Type: application/json
Date: Fri, 22 Feb 2019 12:24:52 GMT
Server: gunicorn/19.9.0

{
    "id": "77c059e7a4d740ed9416e285c8d57b04",
    "phone": "+358456315",
    "timestamp": "2019-02-22 12:11:04.000",
    "username": "user1"
}



And see the log using slave DB]


then you can do 
> docker ps

➜  eleanor_project git:(master) docker ps
CONTAINER ID        IMAGE                           COMMAND                  CREATED             STATUS                         PORTS                               NAMES
e0bb430f4b01        eleanor_project_eleanor-api     "python3 create_db.py"   7 minutes ago       Restarting (0) 9 seconds ago                                       eleanor_project_eleanor-api_run_42debbde7393
e6fe894a31c7        eleanor_project_eleanor-tasks   "/usr/local/bin/cele…"   7 minutes ago       Up 7 minutes                                                       eleanor_project_eleanor-tasks_1
4f58ad0c5ffe        eleanor_project_eleanor-api     "/usr/local/bin/guni…"   7 minutes ago       Up 7 minutes                   0.0.0.0:80->5000/tcp                eleanor_project_eleanor-api_1
d7d93539d3c4        adhorn/mysql:5.7-replica        "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   33060/tcp, 0.0.0.0:3307->3306/tcp   slave
9c622d88ab7b        adhorn/mysql:5.7-replica        "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   0.0.0.0:3306->3306/tcp, 33060/tcp   master
a545b12642cc        redis:latest                    "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   6379/tcp                            eleanor_project_redis_1


and pause the master DB

➜  eleanor_project git:(master) docker pause 9c622d88ab7b
9c622d88ab7b


and still do the same get users.


and you can play with tasks 

➜  ~ http PUT http://127.0.0.1:80/api/task
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 80
Content-Type: application/json
Date: Fri, 22 Feb 2019 12:27:17 GMT
Server: gunicorn/19.9.0

{
    "Status": "Up and running!",
    "Task ID": "98ac26f7-c2d6-4600-8246-d2262ecae7fd"
}

and see the log with the expo backoff



eleanor-tasks_1  | [2019-02-21 10:44:42,911: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:43,879: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 2s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:45,882: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 5s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:50,888: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 12s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:45:02,893: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 96s: ValueError('empty range for randrange()',)


➜  ~ http GET http://127.0.0.1:80/api/task/98ac26f7-c2d6-4600-8246-d2262ecae7fd
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 49
Content-Type: application/json
Date: Fri, 22 Feb 2019 12:28:01 GMT
Server: gunicorn/19.9.0

{
    "Status": "Up and running!",
    "Task ID": "RETRY"
}




DONE:
- Async pattern - API <> WORKERS

- Retries with expo backoff + Jitter
        > http PUT http://127.0.0.1:80/api/add
        watch the log with backoff retry

TODO:
- Health Check
- Degradation read-only mode
- Degradation of the read replica - move the read to master ...

