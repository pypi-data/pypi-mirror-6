django-admin-sortable2
======================

Generic drag-and-drop ordering for objects in the Django admin interface
------------------------------------------------------------------------

Project home: https://github.com/jrief/django-admin-sortable2

Ask questions and report bugs on: https://github.com/jrief/django-admin-sortable2/issues

Introduction
------------
This is another generic drag-and-drop ordering module for sorting objects in the list view
of the Django admin interface. It is a rewrite of
[django-admin-sortable](https://github.com/iambrandontaylor/django-admin-sortable)
using an unintrusive approach.

This plugin offers simple mixin classes which augment the functionality of *any* existing class
derived from ```admin.ModelAdmin```, ```admin.StackedInline``` or ```admin.TabluarInline```. It thus
makes it very easy to integrate with existing models and their model admin interfaces.

These admin mixin classes slightly modify the admin views of a sortable model. There is no need
to derive your model class from a special base model class. You can use your existing ordered field,
just as you always did, or add a new one with any name you like, if needed.

Build status
------------
[![Build Status](https://travis-ci.org/jrief/django-admin-sortable2.png?branch=master)](https://travis-ci.org/jrief/django-admin-sortable2)

Installation
------------
The latest stable release from PyPI:

```pip install django-admin-sortable2```

or the current development release from github:

```pip install -e git+https://github.com/jrief/django-admin-sortable2#egg=django-admin-sortable2```

In ``settings.py`` add:

```python
INSTALLED_APPS = (
    ...
    'adminsortable',
    ...
)
```

Integrate your models
---------------------
Each database model which shall be sortable requires a position value in its model description.
Rather than defining a base class, which contains such a positional value in a hard coded field,
this plugin lets you reuse existing sort fields or define a new field for the sort value.
Therefore this plugin can be applied in situations where your model is derived from an existing
abstract model which already contains any kind of position value. The only requirement for this
plugin is that this position value be specified as the primary field used for sorting. This in
Django is declared through the model's Meta class. Example ``models.py``:

```python
class SortableBook(models.Model):
    title = models.CharField('Title', null=True, blank=True, max_length=255)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ('my_order',)
```

Here the ordering field is named ```my_order```, but any other name is valid. There are only
two requirements:

1) ```my_order``` is the first field in the ```ordering``` tuple of the model's Meta class.
2) ```my_order```'s default value must be 0. The javascript which performs the sorting is
1-indexed, so this will not interfere with the order of your items, even if you're already
using 0-indexed ordering fields.

The field used to store the ordering position may be any kind of numeric model field offered by
Django. Use one of these models fields:
* ```models.BigIntegerField```
* ```models.IntegerField```
* ```models.PositiveIntegerField``` (recommended)
* ```models.PositiveSmallIntegerField``` (recommended for small sets)
* ```models.SmallIntegerField```

These model fields also work, but are not recommended:
* ```models.DecimalField```
* ```models.FloatField```

**Warning:** Do not make this field unique!

Make a list view sortable
-------------------------
Next to the action checkbox, a draggable area is added to each entry line. The user than may click
on any item and vertically drag that item to a new position.

![Sortable List View](docs/list-view.png)

If one or more items shall be moved to another page, this can easily been done by selecting them
though the action checkbox. Then the user shall click on a predefined action from the pull down
menu on the top of the list view.

Integrate into a list view
--------------------------
In ```admin.py```, add a mixin class to augment the functionality for sorting (be sure to put the
mixin class before model.ModelAdmin):

```python
from django.contrib import admin
from adminsortable.admin import SortableAdminMixin
from models import MyModel

class MyModelAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass
admin.site.register(MyModel, MyModelAdmin)
```

That's it! The list view of the model admin interface now adds a column with a sensitive area. By
clicking on that area, the user can move that row up or down. If he wants to move it to another
page, he can do that as a bulk operation, using the admin actions.

Make a stacked or tabular inline view sortable
----------------------------------------------
The interface for a sortable stacked inline view looks exactly the same. If you click on an
stacked inline's field title, this whole inline form can be moved up and down.

The interface for a sortable tabular inline view adds a sensitive area to each draggable row. These
rows then can be moved up and down.

![Sortable Tabular Inlines](docs/tabular-inline.png)

After moving a tabular or stacked inline, save the model form to persist its sorting order.

Integrate into a detail view
----------------------------

```python
from django.contrib import admin
from adminsortable.admin import SortableInlineAdminMixin
from models import MySubModel, MyModel

class MySubModelInline(SortableInlineAdminMixin, admin.TabularInline):  # or admin.StackedInline
    model = MySubModel

class MyModelAdmin(admin.ModelAdmin):
    inlines = (MySubModelInline,)
admin.site.register(MyModel, MyModelAdmin)
```

Initial data
------------
In case you just changed your model to contain an additional sorting field (e.g. ``my_order``), which
does not yet contain any values, then you may set initial ordering values by pasting this code
snippet into the Django shell:

```python
shell> ./manage.py shell
Python ...
>>>
from myapp.models import *
order = 0
for obj in MySortableModel.objects.all():
    order += 1
    obj.my_order = order
    obj.save()
```

or using South migrations:

```python
shell> ./manage.py datamigration myapp set_order
```

this creates an empty migration named something like ```migrations/0123_set_order.py```. Edit
the file and change it into a data migration:

```python
class Migration(DataMigration):
    def forwards(self, orm):
        order = 0
        for obj in orm.MyModel.objects.all():
            order += 1
            obj.my_order = order
            obj.save()
```

then apply the changes to the database using:

```
shell> ./manage.py migrate myapp
```

Run Example Code
----------------
To get a quick first impression of this plugin, clone this repositoty from GitHub and run an
example webserver:

```
git clone https://github.com/jrief/django-admin-sortable2.git
cd django-admin-sortable2/example/
./manage.py syncdb
# add an admin user
./manage.py loaddata testapp/fixtures/data.json
./manage.py runserver
```

Point a browser onto [http://localhost:8000/admin/](http://localhost:8000/admin/), log in and
go to *Sortable books*. There you can test the behaviour.

Note on unique indices on the position field
--------------------------------------------
From a design consideration, one might be tempted to add a unique index on the ordering field. But
in practice this has serious drawbacks:

MySQL has a feature (or bug?) which requires to use the ```ORDER BY``` clause in bulk updates on
unique fields.

SQLite has the same bug which is even worse, because it does neither update all the fields in one
transaction, nor does it allow to use the ```ORDER BY``` clause in bulk updates.

Only PostgreSQL does it "right" in the sense, that it updates all fields in one transaction and
afterwards rebuilds the unique index. Here one can not use the ```ORDER BY``` clause during updates,
which is senseless anyway.

See https://code.djangoproject.com/ticket/20708 for details.

Therefore I strongly advise against setting ```unique=True``` on the position field, unless you want
unportable code, which only works with Postgres databases.

Why another plugin?
-------------------
All available plugins which add functionality to make list views for the Django admin interface
sortable, offer a base class to be used instead of ```models.Model```. This abstract base class then
contains a hard coded position field, additional methods, and meta directives. The problem with such
an approach is twofold. First, an IS-A relationship is abused to augment the functionality of a class.
This is bad OOP practice. A base class shall only be used to reflect a real IS-A relation which
specializes this class. For instance: A mammal **is an** animal, a primate **is a** mammal,
homo sapiens **is a** primate, etc. Here the inheritance model is appropriate, but it would be wrong
to derive from homo sapiens to reflect a human which is able to hunt using bows and arrows.

So, a sortable model **is not an** unsortable model. Making a model sortable augments its
functionality. In OOP design this does not qualify for an IS-A relationship.

Fortunately, Python makes it very easy to distinguish between real IS-A relationships and augmenting
functionalities. The latter are handled by mixin classes. They offer additional functionality
for a class without deriving from the base class.

Also consider the case when someone wants to augment some other functionality of a model class.
If he also derives from ```models.Model```, he would create another abstract intermediate class.
Someone who wants to use **both** functional augmentations is now in trouble. He has to choose
between one of the two, as he cannot dervie from them both, because his model class would inherit
the base class ```models.Model``` twice. This kind of diamond-shaped inheritance is to be avoided
under all circumstances.

By using a mixin class rather than deriving from a special abstract base class, these problems
can be avoided!

Related projects
================
* https://github.com/iambrandontaylor/django-admin-sortable
* https://github.com/mtigas/django-orderable
* http://djangosnippets.org/snippets/2057/
* http://djangosnippets.org/snippets/2306/
* http://catherinetenajeros.blogspot.co.at/2013/03/sort-using-drag-and-drop.html

Release history
===============
* 0.2.6 Fixed: Unsortable inline models become draggable when there is a sortable inline model
* 0.2.5
 * Bulk actions are added only when they make sense.
 * Fixed bug when clicking on table header for ordering field.
* 0.2.4 Fix CustomInlineFormSet to allow customization. Thanks **yakky**.
* 0.2.2 Distinction between different versions of jQuery in case django-cms is installed side by side.
* 0.2.0 Added sortable stacked and tabular inlines.
* 0.1.2 Fixed: All field names other than "order" are now allowed.
* 0.1.1 Fixed compatibility issue when used together with django-cms.
* 0.1.0 first version published on PyPI.
* 0.0.1 first working release.

License
-------
Copyright &copy; 2014 Jacob Rief. Licensed under the MIT license.
