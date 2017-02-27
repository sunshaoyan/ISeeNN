# The Introduction to ISeeNN System

This is a comprehensive document about our CNN based image retrieval system __ISeeNN__ building procedure.

The phrase **ISeeNN** can be expanded as *I See (with) CNN*.

We provide an online demo [here](http://222.195.92.10:8000/search_web), which indexes [MirFlickr 1M dataset](http://press.liacs.nl/mirflickr/). It is only for demonstration purpose, and may not be always available.

## System Overview
The system consists of __three__ principal components:

- A distributed __Image Serving__ system
- A __Search Engine__ for running retrieval
- A __Front End__ for user interaction

The system is featured in:

- Support multiple CNN models, feature types with dynamic switch
- Support index update with new queries
- Support specifying dataset coverage
- Support user session to record feedback
- Open API for new algorithms
- Support image URL distribution from multiple internal servers

The framework of our system can be illustrated as:
![](img/framework.png)

## Setup
In this part, I will show the system setup details. 

Our system is built upon a number of linux servers. Essentially, **ISeeNN** is not a distributed system, but only with supporting of image storage and fetch from multiple servers.

Here is the configuration of our premier implement:

| ID | Operating System | Role | Internal IP | GPU | Memory |
|:---------:|------------------|------|-------------|---|:---:|
| 1 | Ubuntu 14.04 x64 | Front End & Retrieval System & Mongo Server | 192.168.6.232 | K80 x 4 | 64G |
| 2 | Open Suse 13.2 x64 | Image Server | 192.168.104.244 | K40 x 2 | 64G |
| 3 | Open Suse Leap 42.1 x64 | Image Server | 192.168.102.200 | GeForce GTX 660 Ti | 16G |

It can be seen that we do not rely on the very same operating system for different servers. We choose **Server 1** as the principal server because it has relatively higher computing resource. Of course it can also serve as an image server.

In the following we first focus on the configurations on **Server 1**.

### Database Setting
We use [MongoDB](https://www.mongodb.com) v3.4.1 as the backend storage database. Contents in the database include:

- index of the image dataset (``feature_id -> image_id``)
- image distribution information (``image_id -> image_url``)


Because the apt repository is old for MongoDB, we directly download the binary files.

```bash
$ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.4.1.tgz
$ tar zxvf mongodb-linux-x86_64-ubuntu1404-3.4.1.tgz
$ sudo cp mongodb-linux-x86_64-ubuntu1404-3.4.1/bin/* /usr/local/bin
```
To initialize the database, we first create admin users for the ***admin*** and our ***image_retrieval*** database.

We use the script written by [frodenas](https://github.com/frodenas/docker-mongodb/blob/master/scripts/first_run.sh) for the initialization. 

```bash
# first_run.sh
#!/bin/bash
 USER=${MONGODB_USERNAME:-mongo}
 PASS=${MONGODB_PASSWORD:-$(pwgen -s -1 16)}
 DB=${MONGODB_DBNAME:-admin}
 DBPATH=/db/mongo # set your own db_path here
 if [ ! -z "$MONGODB_DBNAME" ]
 then
     ROLE=${MONGODB_ROLE:-dbOwner}
 else
     ROLE=${MONGODB_ROLE:-dbAdminAnyDatabase}
 fi

 # Start MongoDB service
 mongod --dbpath $DBPATH --nojournal &
 while ! nc -vz localhost 27017; do sleep 1; done

 # Create User
 echo "Creating user: \"$USER\"..."                                                                           
 mongo $DB --eval "db.createUser({ user: '$USER', pwd: '$PASS', roles: [ { role: '$ROLE', db: '$DB' } ] }); "
 
 # Stop MongoDB service
 mongod --dbpath $DBPATH --shutdown                                                                                                                                                                                     
 echo "MongoDB User: \"$USER\""
 echo "MongoDB Password: \"$PASS\""
 echo "MongoDB Database: \"$DB\""
 echo "MongoDB Role: \"$ROLE\""
```

First, create a admin user for the ***admin*** database, by

```bash
$ ./first_run.sh
MongoDB User: "mongo"
MongoDB Password: "xxxxxxxxxxxxx"
MongoDB Database: "admin"
MongoDB Role: "dbAdminAnyDatabase"
```

Then, create a *dbOwner* user for the ***image_retrieval*** database, by

```bash
$ export MONGODB_USERNAME=webclient
$ export MONGODB_DBNAME=image_retrieval
$ ./first_run.sh
MongoDB User: "webclient"
MongoDB Password: "xxxxxxxxxxxxx"
MongoDB Database: "image_retrieval"
MongoDB Role: "dbOwner"
```
Here I hided the password. Remember to save the user information for further use.

After the initialization, start the mongod server with config file
``/db/mongodb.conf``

```bash
# /db/mongodb.conf
dbpath=/db/mongo/
logpath=/db/mongodb.log
logappend=true
journal=true
auth = true
```

```bash
$ mongod --config /db/mongodb.conf
```

Now test your database

```bash
$ mongo
MongoDB shell version v3.4.1
connecting to: mongodb://127.0.0.1:27017
MongoDB server version: 3.4.1
> use image_retrieval
switched to db image_retrieval
> db.auth('webclient', 'xxxxxxxxxxx')
1
```

### Django Development Environment

We use Python3 to develop the web service, and to extract CNN features with [Tensorflow](https://www.tensorflow.org) Python interface.

In this part we will config Python with Django module for web service and its MongoDB backend 

It is benificial to create standalone python runtime environment with [virtualenv](https://virtualenv.pypa.io/en/stable/).

Install ``virtualenv``:

```bash
$ sudo pip install virtualenv
```

Now in your workspace, create and enter a virtualenv environment:

```bash
$ virtualenv --no-site-packages -p python3 image_retrieval
$ cd image_retrieval
$ source bin/activate
```

Setup [Django](https://www.djangoproject.com), [MongoEngine](http://mongoengine.org), [ski-image](http://scikit-image.org) and [Pillow](http://pillow.readthedocs.io/en/latest/#):

```bash
$ pip install django
$ pip install mongoengine
$ pip install scikit-image
$ pip install Pillow
```

Then setup your [TensorFlow](https://www.tensorflow.org) under the instruction of the website.

Now we have Python environment as (depending on your own environment):

```bash
$ pip freeze
appdirs==1.4.0
cycler==0.10.0
dask==0.13.0
decorator==4.0.11
Django==1.10.5
matplotlib==2.0.0
mongoengine==0.11.0
networkx==1.11
numpy==1.12.0
olefile==0.44
packaging==16.8
Pillow==4.0.0
protobuf==3.2.0
pymongo==3.4.0
pyparsing==2.1.10
python-dateutil==2.6.0
pytz==2016.10
scikit-image==0.12.3
scipy==0.18.1
six==1.10.0
tensorflow-gpu==0.12.1
toolz==0.8.2
```

And let's start our **ISeeNN** project:

```bash
$ django-admin startproject ISeeNN
$ tree ISeeNN
ISeeNN
├── ISeeNN
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

To work with the MongoDB backend, modify the ``DATABASE`` setting in ``ISeeNN/settings.py`` as:

```python
import mongoengine
...
DATABASES = {
    'default': {
        'ENGINE': '',
    }
}

_MONGODB_USER = 'webclient'
_MONGODB_PASSWD = 'xxxxxxxxxxxxxx'
_MONGODB_HOST = '192.168.6.232'
_MONGODB_NAME = 'image_retrieval'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)

```

And configure the ``TIMEZONE = 'Asia/Shanghai'``.

Due to the weak support of Django for MongoDB, we are not using the admin component for this version. So let's comment the related code in ``urls.py``

```python
from django.conf.urls import url
# from django.contrib import admin

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
]
```

OK! now lanch the server by

```bash
./manage.py runserver 8000
```

Then open your browser to browse ``http://localhost:8000`` to test it.

### Boost Python Wrapper
Our search engine backend is implemented with C++ for efficiency concern. To call this backend, we wrap the C++ code with Boost Python to be exposed as a Python module.

Make sure to install boost-dev and boost-python-dev with python 3 support.

For Ubuntu:

```bash
$ sudo apt-get install libboost-dev libboost-python-dev
```

For OSX: (it's important to set the flags below)

```bash
$ brew install boost
$ brew install boost-python --with-python3 --without-python
```

For Suse Linux:

```
$ sudo zypper in boost-devel
```

To use these libraries, add these lines to your CMakeLists.txt:

```c
INCLUDE(FindPythonLibs)
FIND_PACKAGE(PythonInterp)
FIND_PACKAGE(PythonLibs)
FIND_PACKAGE(Boost COMPONENTS python3)

INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})
LINK_LIBRARIES(${Boost_LIBRARIES} ${PYTHON_LIBRARIES})

PYTHON_ADD_MODULE(your_target ${SOURCE_FILES})
```

## To run the project

There are three parts in this project: 

* the web interface ``ISeeNN/``, including two web apps ``search_web/`` and ``image_server/``.
* the indexer ``Indexer/`` that runs off-line, to index specifical image dataset into the database.
* the search engine ``search_engine/`` implemented wit C++, which will be compiled to shared library to be used as a Python module in the web interface.

To run the project, follow these steps:

* setup environment as the previous chapter.
* copy ``ISeeNN/IseeNN/personal_settings.py.example`` to ``ISeeNN/IseeNN/personal_settings.py``
* specify the mongodb user name and password in the above setting file and ``Indexer/indexer.py``
* create ``image_server`` documents in your mongo shell. e.g.,

```bash
> db.image_server.insert({server_name: 'Amax', server_ip: '192.168.104.244'})
```

* index your target image dataset in local disks.

	1) set the ``dir_name = ''``, ``server_name=''`` in ``Indexer/indexer.py``. Maybe you also want to specify normalizer type and model type. Currently this script is not well organized. We will make a revision in the future.
	
	2) run ``cd Indexer && python indexer.py``
	
* compile and install the search engine backend:

```bash
$ cd search_engine && ./build.sh
```

* run the server

```bash
$ cd ISeeNN && ./manager.py runserver 0.0.0.0:8000
```

* Have fun!
