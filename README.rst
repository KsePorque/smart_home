Smart House
==============
Project was made as a final task for Coursera course.
And later it was improved with some additional features.


Установка
---------

Установите pipenv

.. code-block:: bash

    $ pip install pipenv


Установите зависимости проекта, включая зависимости для разработки

.. code-block:: bash

    $ pipenv install --dev

Активируйте virtualenv проекта

.. code-block:: bash

    $ pipenv shell

Запустите миграции

.. code-block:: bash

    $ python manage.py migrate


Запуск
------

На главной странице сервиса будет расположена панель управления вашим умным домом.

Для запуска периодического опроса состояния дома, используется celery.

Она запускается как celery -A coursera_house.celery worker -l info -B

Celery использует Redis как брокер

Тестирование
------------
Для запуска тестов выполните команду

.. code-block:: bash

    $ py.test tests
