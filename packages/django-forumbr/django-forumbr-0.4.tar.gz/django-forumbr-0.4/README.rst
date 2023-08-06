Django ForumBR
==============

**A simple, everyday django forum**

Django-forumbr is a project to create a simple, easy-to-use and complete forum
for django projects on the run.

Releases
--------

* django-forumbr 0.4 (23/04/2014): Compatible with Django 1.6
* django-forumbr 0.3.1.3 (15/12/2012): Compatible with Django 1.3/1.4

Install instructions
--------------------
    pip install django-forumbr

    # then add forum to your settings INSTALLED_APPS
    # and url(r'^forum/', include('forum.urls', namespace='forum')) to your urls.py

    # create the models and you're done
    python manage.py syncdb

Optional
--------
    ForumBR uses a set of libraries to provide text formatting support.
    The default formatting syntax for replies is plain text.
    To turn on the support, install the disired library:

    pip install bbcode
    pip install markdown
    pip install textile
    pip install docutils
    pip install html5lib # for plain html support

    and then, set the FORUM_MARKUP language of your choice.

App Settings
------------
ForumBR comes with a large set of configurable settings. For a complete list of options,
take a look at **django-forumbr/app_settings**.

Auth
----
See **django-forum/test_project** for an example on how
to integrate with django-registration.
