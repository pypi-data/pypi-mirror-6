Installation instructions
=========================

If you're used to play with pip_ and virtualenv_ the install process should be
quite easy for you.

.. contents::

.. _install_dependencies:

Dependencies
------------

To install Django-rblog the main dependencies are the following:

* Django_
* Pygments_
* South_
* PIL_
* django-tinymce_
* django-tagging_
* sorl-thumbnail_

This packages deppends on other thirds. You can see the complete list in the
``setup.py`` file. If you're using pip to install this piece of software you
don't have to worry about the dependencies, pip_ do the job.

.. _virtualenv:

Installation
------------

You can install django-rblog in two different ways, with pip or cloning the
oficial repository and hook it to your project with python develop option.

With pip
^^^^^^^^

To install django-rblog with pip_ it's as easy as run this command on your
enviroment::

    $ pip install django-rblog

Cloning the repo
^^^^^^^^^^^^^^^^

We recommend you to create a virtualenv and run your django-rblog based
project into them. To create a virtualenv you must follow this steps (asumming
pip and virtualenv installed in your computer)::

    $ hg clone https://bitbucket.org/r0sk/django-rblog your/local/path

And that's all, the Django-rblog was successfully installed on your
computer.

Project from scratch
--------------------

Well, it's not too util to know how to install django-rblog if you don't know
how to integrate it in a project. So let me explain how to install this
software in a projec, from scratch.

First of all you create a virtualenv_ and install Django_::

    $ mkdir myblog
    $ cd myblog
    $ virtualenv env
    New python executable in env/bin/python
    Installing setuptools............done.
    Installing pip...............done.
    $ . env/bin/activate
    (env)$ pip install "Django<1.5"

Once we have Django_ installed we are going to install django-rblog, we can do
it with one of the methods we describe above:

Pip method
^^^^^^^^^^
::

    $ . env/bin/activate
    (env)$ pip install django-rblog
    Downloading/unpacking django-rblog
    [it will resolve the dependencies...]

Cloning develop repo
^^^^^^^^^^^^^^^^^^^^
::

    $ . env/bin/activate
    (env)$ hg clone https://bitbucket.org/r0sk/django-rblog django-rblog
    (env)$ cd django-rblog
    (env)$ python setup.py develop

At this time we have our myblog project ready to run django-rblog, next step is
to start the project and tune the settings.

Start the project
^^^^^^^^^^^^^^^^^

Once you have installed Django and django-rblog, you have to start and
configure a Django project, let's go::

    (env)$ django-admin.py startproject project

Now you have to configure the database backend and the other general values you
are used to configure in a Django project. Next step is to add the ``rblog``
and all the required apps to INSTALLED_APPS config directive::

    INSTALLED_APPS += ('south',
                       'tinymce',
                       'filebrowser',
                       'tagging',
                       'sorl.thumbnail',
                       'disqus',
                       'compressor',
                       'rblog', )

And lastly we have to create the project database and migrate it to last
django-rblog version::

    (env)$ ./manage.py syncdb
    [Create a Django superuser]

::

    (env)$ ./manage.py migrate rblog --list
     rblog
      ( ) 0001_initial
      ( ) 0002_auto__del_comments__del_field_post_thread_id
      ( ) 0003_auto__add_comments__add_field_post_thread_id
      ( ) 0004_auto__chg_field_post_creation_date
      ...
    (env)$ ./manage.py migrate rblog

ERROR MPTT


Configure the project
^^^^^^^^^^^^^^^^^^^^^




.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Django: http://djangoproject.org/
.. _Pygments: http://pygments.org/
.. _South: http://south.aeracode.org/
.. _PIL: http://www.pythonware.com/products/pil/
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-tagging: https://code.google.com/p/django-tagging/
.. _sorl-thumbnail: http://sorl-thumbnail.readthedocs.org/en/latest/
