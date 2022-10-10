Smart House
==============
Project was made as a final task for the coursera course<br>
<strong>Task</strong>: to implement the operational logic of smart house. <br>
The Smart House has approximately 20 sensors, that show what devices are on (washing machine, boiler, air conditioning, etc). 
The implemented logic should control the smart house. For example, turn off devices if smoke is detected, turn on boiler for heating water, curtains closure/opening for automatic control over room illumination.
<br><br> 

Before running
=============
You have to create an account for smart house: http://smarthome.webpython.graders.eldf.ru<br>
Then, several environment variables should be established:
- SMART_HOME_ACCESS_TOKEN (required; token to access sensors info of the smart house)
- EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_RECEPIENT,EMAIL_USE_SSL  (not required;. for sending email notifications in case server is not accessible)

Docker
=============
Project contains docker files to run application in containers

.. code-block:: bash
    
    $ docker-compose build
    
.. code-block:: bash
    
    $ docker-compose up -d


After this is done the network with several containers will be established

The main page of this service has the panel to control parameters of the house, such as hot water temperature, room temperature and lights: http://localhost:8080<br>
Automatic sensors data checks and turning the devicas on/off is implemented using celery


Installation via pipenv
---------
As an alternative, installation via pipenv is available<br>
Install pipenv

.. code-block:: bash

    $ pip install pipenv


Install project dependencies

.. code-block:: bash

    $ pipenv install --dev

Activate virtualenv 

.. code-block:: bash

    $ pipenv shell

Run migrations

.. code-block:: bash

    $ python manage.py migrate

Run server
.. code-block:: bash

    $ python manage.py runserver 127.0.0.1:8080


To run periodic checks of smart houses devices celery is used.<br> 
To start automatic tasks: celery -A coursera_house.celery worker -l info -B

Celery uses Redis as a broker


Testing
------------
To run tests

.. code-block:: bash

    $ py.test tests
