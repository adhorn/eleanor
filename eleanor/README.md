

**eleanor**:

Demo and code I use to go along my talk on patterns for building resilient applications on AWS. 

Added the SQL databases (mysql-data, and mysql-dataread) used by docker. 
Both DBs are the same - i just simply altered on field to show the read and write diff. 
I did on the read DB:
> UPDATE users SET username = 'adrian' WHERE username = 'user1';



DONE:
- Async pattern - API <> WORKERS

- Retries with expo backoff + Jitter
        > http PUT http://127.0.0.1:80/api/add
        watch the log with backoff retry

eleanor-tasks_1  | [2019-02-21 10:44:42,911: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 1s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:43,879: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 2s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:45,882: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 5s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:44:50,888: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 12s: ValueError('empty range for randrange()',)
...
eleanor-tasks_1  | [2019-02-21 10:45:02,893: INFO/MainProcess] Task eleanor.celery.tasks.add[26a1c4fd-db90-475a-a1d2-005ae176162b] retry: Retry in 96s: ValueError('empty range for randrange()',)


- Read Write separation:
      - use docker pause on master db 
        > docker pause a33c2a780d61
        > http GET http://127.0.0.1/api/user/a47d9ebdb66f4315816622ad26203ab3 - that will work
        > docker unpause a33c2a780d61


TODO:
- Health Check
- Degradation read-only

