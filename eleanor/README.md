

**eleanor**:

Demo of the asynchronous worker pattern using Flask and Celery.


**Why this demo?**:

While Flask + Celery code is very common on the internet, I could not find any ready-to-use example which would combine all the bells and whistles necessary to run the asynchronous pattern code in production. This code here gives you just that (hopefully).
This demo also uses Gunicorn to serve the Flask application.


**Asynchronous Pattern on AWS**:

![Architecture](https://github.com/adhorn/eleanor/blob/master/pics/demo1.png)

![How it works (part1)](https://github.com/adhorn/eleanor/blob/master/pics/demo2.png)

![How it works (part2)](https://github.com/adhorn/eleanor/blob/master/pics/demo3.png)


**What is Flask?**: 
Flask is a fun and easy to use microframework for Python based on Werkzeug.
It is easy to setup and use, and has a large community, lots of examples, etc:

```
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
```

```
$ python hello.py
 * Running on http://localhost:5000/
```

**What is Gunicorn?**
Gunicorn 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. It's a pre-fork worker model. The Gunicorn server is broadly compatible with various web frameworks, simply implemented, light on server resources, and fairly speedy.


**What is Celery?**
Celery is an asynchronous task queue/job queue based on distributed message passing. It is focused on real-time operation, but supports scheduling as well. 
The execution units, called tasks, are executed concurrently on a single or more worker servers using multiprocessing, Eventlet,	or gevent. Tasks can execute asynchronously (in the background) or synchronously (wait until ready).
Celery is used in production systems to process millions of tasks a day.






