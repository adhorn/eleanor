# Eleanor-Project

Eleanor-Project is a set of project used to run and demo Eleanor

**Folders**:

`/eleanor` contains the Python Application

`/nginx` contains the load balancer configuration

`/chaos` contains an example chaos experiment using ChaosToolkit

`/mysql-replica` is a fork of `https://github.com/twang2218/mysql-replica` 


**Prerequisites**:

To use and run Eleanor, you need to have docker installed locally. The application is built using docker-compose.

You also need a python virtual environment in which you have installed all the `/eleanor_project/elanor/requirements.txt`

For python virtual environments, I use `pyenv`

```bash
> pyenv virtualenv eleanor
(eleanor) > pip install -r requirements.txt
```

To run the application, open a terminal in you local machine (Mac, Linux or Windows) and run `docker-compose up` this will built and run a set of  docker containers found in `/elanor_project/docker-compose.yml`.

```bash
> cd eleanor_project
> docker-compose up 
```

Once the application is built and runs (this may take a while when you do it for the first time), you need to initialise the database. 
To do that, open another terminal and run:  

```bash
> docker-compose run eleanor-api python3 create_db.py
```
