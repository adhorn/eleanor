

**eleanor**:

Demo and code I use to go along my talk on patterns for building resilient applications on AWS. 


To Get started, open a terminal and run - this will start all the docker containers found in docker-compose.yml


> docker-compose up 


In another terminal, run - this is to create the database table. 

> docker-compose run eleanor-api python3 create_db.py



then you add products:

➜  ~ curl -i -X POST -H "Content-Type: application/json" -d '{ "product_name": "Samsung TV multicolor", "product_type": "consumer good", "price": "564.00" }' http://127.0.0.1:80/api/product
HTTP/1.1 200 OK
Server: nginx/1.15.9
Date: Mon, 18 Mar 2019 15:02:36 GMT
Content-Type: application/json
Content-Length: 71
Connection: keep-alive

{"product_id": "691d0791388243a3b00558c03c70768f", "status": "success"}%

In the screen log where you are executing docker-compose, you can monitor that the API is putting the data in the Master
Logs look like that:

eleanor-api_1    | --------------------------------------------------------------------------------
eleanor-api_1    | DEBUG in __init__ [/opt/eleanor/eleanor/db/__init__.py:43]:
eleanor-api_1    | Connecting -> MASTER
eleanor-api_1    | --------------------------------------------------------------------------------




You can then verify in the DBs using the mysql tool that the data is being replicated. 

Master:

MySQL  127.0.0.1:3306 ssl  mysql  SQL > select * from products;
+----------------------------------+---------------------+------------------------+---------------+--------+
| id                               | timestamp           | product_name           | product_type  | price  |
+----------------------------------+---------------------+------------------------+---------------+--------+
| 691d0791388243a3b00558c03c70768f | 2019-03-18 15:02:36 | Samsung TV multicolo9r | consumer good | 564.00 |
+----------------------------------+---------------------+------------------------+---------------+--------+
1 row in set (0.0034 sec)



Slave:

MySQL  127.0.0.1:3307 ssl  mysql  SQL > select * from products;
+----------------------------------+---------------------+------------------------+---------------+--------+
| id                               | timestamp           | product_name           | product_type  | price  |
+----------------------------------+---------------------+------------------------+---------------+--------+
| 691d0791388243a3b00558c03c70768f | 2019-03-18 15:02:36 | Samsung TV multicolo9r | consumer good | 564.00 |
+----------------------------------+---------------------+------------------------+---------------+--------+
1 row in set (0.0026 sec)




Fetch a particular product using the GET product API:

➜  ~ http get http://127.0.0.1:80/api/product/691d0791388243a3b00558c03c70768f
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 176
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:02:54 GMT
Server: nginx/1.15.9

{
    "id": "691d0791388243a3b00558c03c70768f",
    "price": "564.00",
    "product_name": "Samsung TV multicolo9r",
    "product_type": "consumer good",
    "timestamp": "2019-03-18 15:02:36.000"
}


In the screen log where you are executing docker-compose, you can monitor that the API is fetch the data from the Slave

Logs look like that.
eleanor-api_1    | --------------------------------------------------------------------------------
eleanor-api_1    | DEBUG in __init__ [/opt/eleanor/eleanor/db/__init__.py:61]:
eleanor-api_1    | Connecting -> SLAVE
eleanor-api_1    | --------------------------------------------------------------------------------



HealthChecks
-------------

Shallow health check:

➜  ~ http get http://127.0.0.1:80/api/echo
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 29
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:11:26 GMT
Server: nginx/1.15.9

{
    "Status": "Up and running!"
}

This will work regardless if any dependencies are up. Good for fast checks and recovering from outages.


Deep health check:
This health check supports Caching - hit it several times in a row, the content is served from the cache - preserving resources.


➜  ~ http get http://127.0.0.1:80/api/health
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 924
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:12:32 GMT
Server: nginx/1.15.9

{
    "hostname": "172.17.0.7",
    "results": [
        {
            "checker": "db_master_check",
            "expires": 1552921967.4426348,
            "output": "db master ok",
            "passed": true,
            "timestamp": 1552921952.4426348
        },
        {
            "checker": "db_slave_check",
            "expires": 1552921967.4513915,
            "output": "db slave ok",
            "passed": true,
            "timestamp": 1552921952.4513915
        },
        {
            "checker": "redis_check",
            "expires": 1552921967.4776466,
            "output": "redis ok",
            "passed": true,
            "timestamp": 1552921952.4776466
        },
        {
            "checker": "task_check",
            "expires": 1552921967.544384,
            "output": "tasks ok",
            "passed": true,
            "timestamp": 1552921952.544384
        }
    ],
    "status": "success"
}


Tasks:
------

Normal one - successful to demo the async queue pattern

➜  ~ http PUT http://127.0.0.1:80/api/task
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 51
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:14:06 GMT
Server: nginx/1.15.9

{
    "Task ID": "0a09135f-d053-49e6-a114-43b7b51eec3e"
}


Task with retries every 1s (dangerous)

➜  ~ http PUT http://127.0.0.1:80/api/taskretry
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 51
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:14:33 GMT
Server: nginx/1.15.9

{
    "Task ID": "7c3a55a0-dcb7-4e73-b481-d7f76f2b7b75"
}

eleanor-tasks_1  | [2019-03-18 15:18:01,874: INFO/MainProcess] Task eleanor.celery.tasks.add_retry[349e045f-cefe-48d6-96b7-6f914f818b88] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-03-18 15:18:01,874: INFO/MainProcess] Task eleanor.celery.tasks.add_retry[349e045f-cefe-48d6-96b7-6f914f818b88] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-03-18 15:18:01,874: INFO/MainProcess] Task eleanor.celery.tasks.add_retry[349e045f-cefe-48d6-96b7-6f914f818b88] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-03-18 15:18:01,874: INFO/MainProcess] Task eleanor.celery.tasks.add_retry[349e045f-cefe-48d6-96b7-6f914f818b88] retry: Retry in 1s: ValueError('empty range for randrange()',)




Task with expo backoff retries (good)

➜  ~ http PUT http://127.0.0.1:80/api/taskexpo
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 51
Content-Type: application/json
Date: Mon, 18 Mar 2019 15:15:03 GMT
Server: nginx/1.15.9

{
    "Task ID": "bcb139ef-776e-43ac-b770-9a20c90080c1"
}

eleanor-tasks_1  | [2019-02-21 10:44:42,911: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:43,879: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 2s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:45,882: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 5s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:50,888: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 12s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:45:02,893: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 96s: ValueError('empty range for randrange()',)



Cool - all works. 

Now lets break things.




In another  terminal - do
> docker ps

this will return the list of running containers.

➜  eleanor_project git:(master) docker ps
CONTAINER ID        IMAGE                           COMMAND                  CREATED             STATUS                         PORTS                               NAMES
e0bb430f4b01        eleanor_project_eleanor-api     "python3 create_db.py"   7 minutes ago       Restarting (0) 9 seconds ago                                       eleanor_project_eleanor-api_run_42debbde7393
e6fe894a31c7        eleanor_project_eleanor-tasks   "/usr/local/bin/cele…"   7 minutes ago       Up 7 minutes                                                       eleanor_project_eleanor-tasks_1
4f58ad0c5ffe        eleanor_project_eleanor-api     "/usr/local/bin/guni…"   7 minutes ago       Up 7 minutes                   0.0.0.0:80->5000/tcp                eleanor_project_eleanor-api_1
d7d93539d3c4        adhorn/mysql:5.7-replica        "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   33060/tcp, 0.0.0.0:3307->3306/tcp   slave
9c622d88ab7b        adhorn/mysql:5.7-replica        "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   0.0.0.0:3306->3306/tcp, 33060/tcp   master
a545b12642cc        redis:latest                    "docker-entrypoint.s…"   7 minutes ago       Up 7 minutes                   6379/tcp                            eleanor_project_redis_1



Try:

1 - stop the master DB and try reading. This will work. 

2 - stop the slave and try reading. This will work IF you make a healthcheck before reading. 
The healthcheck will set env(MASTER) to FORCE if it fails to find the read replica. Here I am explaining the importance of healthcheck returning information that can help degradation.

3 - stop Redis cache - healthcheck will fail. Run healthcheck several time, it will hit the Cache. Important to explain that healthchecks can be dangerous if you have too many probe pinging it - thus the importance of cache. 

4 - stop elanor-task and run http PUT http://127.0.0.1:80/api/task - this will work and succeed once you start the worker again - preserving failures from the client. 











