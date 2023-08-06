django-pgindex
==============

Search for Django and PostgreSQL.


Requirements
------------
* Django >= 1.1
* django-stringfield >= 0.1.5
* django-cerial >= 0.0.2


Installation
------------
First install the package from pypi using pip::

    pip install django-pgindex


Then make ``pgindex`` an app in your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'pgindex',
        ...
    )

Sync your database::

    python manage.py syncdb

Done.

Usage
-----
Create and Index class and register it to your model, much like registering an
admin class to your model. Example::

    # models.py
    from django.db import models
    from .index import ItemIndex
    from pgindex import register

    class Item(models.Model):
        title = models.CharField(max_length=100)
        content = models.TextField()

        def get_absolute_url(self):
            return '/item/'

    register(Item, ItemIndex)


    # index.py
    from pgindex import IndexBase, Vector

    class ItemIndex(IndexBase):
        def get_title(self):
            return self.obj.title

        def get_description(self):
            return self.obj.content

        def get_vectors(self):
            return (
                Vector(self.obj.title, weight='A'),
                Vector(self.obj.content, weight='B'),
            )

To search simply use the ``pgindex.search`` method which returns a queryset
from the ``pgindex.models.Index`` model::

    from pgindex import search

    index_queryset = search('foo')


See tests for examples.


pgindex.IndexBase methods
-------------------------

get_title()
^^^^^^^^^^^
This should return the title of the indexed object.

get_description()
^^^^^^^^^^^^^^^^^
This should return the description of the indexed object.

get_url()
^^^^^^^^^
This should return the url of the indexed object.

get_data()
^^^^^^^^^^
You can return additional data that will be stored in the index field here, this
value will be pickled and depickled.

get_publish()
^^^^^^^^^^^^^^^
If this returns ``False`` and index will not be created

get_start_publish()
^^^^^^^^^^^^^^^^^^^
Can return a ``datetime.datetime`` which is the time when the index will be used.
Returning ``None`` means that it will always be used.

get_end_publish()
^^^^^^^^^^^^^^^^^
Can return a ``datetime.datetime`` which is the time for the index expiration.
Returning ``None`` means that it will never expire.

get_vectors()
^^^^^^^^^^^^^
This method needs to return a list or tuple of ``pgindex.Vector``
instances. This in turn is the base for the text search column.

