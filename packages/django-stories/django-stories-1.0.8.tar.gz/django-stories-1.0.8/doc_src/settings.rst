.. _settings:

========
Settings
========

Here are several settings that you can use to customize Stories. Each of the
following are keys in ``STORY_SETTINGS``\ .

.. contents::
   :local:


.. note:: The settings have been refactored in version 0.8. The old
          settings still work, but raise a ``DeprecationWarning``\ .

.. _status_choices:

STATUS_CHOICES
==============

A story can be in several different states, for example draft vs. live.
Your workflow might have several states that a story goes through, but
there can only be one choice that is considered "Published".

Choices are specified as a ``list`` or ``tuple`` of ``integer`` -
``string`` tuples. The ``integer`` is the code for the choice and the
``string`` is the description that the user sees.

**Defaults:**

.. code-block:: python

	STORY_SETTINGS = {
	    'STATUS_CHOICES': (
	        (1, 'DRAFT'),
	        (2, 'READY FOR EDITING'),
	        (3, 'READY TO PUBLISH'),
	        (4, 'PUBLISHED'),
	        (5, 'REJECTED'),
	        (6, 'UN-PUBLISHED'),
	    )
	}

*Draft:* A work-in-progress.

*Ready for Editing:* The story is ready for an editor's touch.

*Ready to Publish:* The editing is finished and the story is ready to go
on to the web site.

*Published:* The story is on the web site, as long as it is past the
story's publish date and time.

*Rejected:* The editor didn't like something and the author needs to
work on it some more.

*Un-published:* The story has been removed from the site for some reason.

.. _default_status:

DEFAULT_STATUS
==============

When a story is created, what should the the status default to?

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'DEFAULT_STATUS': 1 # Draft
	}

.. _published_status:

PUBLISHED_STATUS
================

Which one of the possible statuses is considered "Show This On Site."

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'PUBLISHED_STATUS': 4 # Published
	}


.. _origin_choices:

ORIGIN_CHOICES
==============

It is possible that stories could be coming in from several sources, such
as a wire service, an editorial front end, or an FTP site. This settings
allows you to mark which stories originated from which source, so you can
potentially do something different depending on the source. For example,
include all stories in the RSS feed, except ones that came from a wire service.

Choices are specified as a ``list`` or ``tuple`` of ``integer`` - ``string``
tuples. The ``integer`` is the code for the choice and the ``string`` is the
description that the user sees.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'ORIGIN_CHOICES': (
	        (0, 'Admin'),
	    )
	}

.. _default_origin:

DEFAULT_ORIGIN
==============

When a story is created from the Django Admin, which choice of origin should
it default to?

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'DEFAULT_ORIGIN': 0 # Admin
	}

.. _include_print:

INCLUDE_PRINT
=============

Should the fields related to print production be included in the database.
The fields are ``print_pub_date``\ , ``print_section``\ , and ``print_page``\ .

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'INCLUDE_PRINT': False
	}

.. _relation_models:

RELATION_MODELS
===============

.. versionchanged:: 1.0
   `relations` is now a seperate app within ``stories``

A story can relate to several other things, such as other stories,
photographs, photo galleries, and external links. Relations links to the
Django Content Types application, which would normally show all sorts of
things that don't matter to the author and end users. This setting
specifies which specific models are relatable to a story.

The value should be a tuple of `'appname.modelname'` strings.

In order to use `Relations`, you must add `stories.relations` to your
**INSTALLED_APPS** and also

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'RELATION_MODELS': [] # Not enabled
	}

.. _pagination:

PAGINATION
==========

Django Stories has a built-in :class:`Paginator` subclass that splits
HTML-formatted text into paragraphs for paginating. The
``DEFAULT_SETTINGS['PAGINATION]`` contains several sub-settings to manage
the process. See :ref:`pagination` for more information, and the
`Django Paginator docs <http://docs.djangoproject.com/en/dev/topics/pagination/#paginator-objects>`_
for more about pagination is general.

.. _paginate:

PAGINATE
********

Should stories be paginated.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'PAGINATION': {
	        'PAGINATE': False
	    }
	}

.. _p_per_page:

P_PER_PAGE
**********

If ``PAGINATE`` is ``True``\ , then this setting sets the number of paragraphs
per page for pagination.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'PAGINATION': {
	        'P_PER_PAGE': 20
	    }
	}

.. _orphans:

ORPHANS
*******

If ``PAGINATE`` is ``True``\ , then this setting sets the minimum number of
paragraphs allowed on the last page for pagination. This means that with
``P_PER_PAGE = 20`` and ``ORPHANS = 4`` a story with 24 paragraphs would
only have one page, but a story with 25 paragraphs would have two pages.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'PAGINATION': {
	        'ORPHANS': 4
	    }
	}

.. _throw_404:

THROW_404
=========

Choose to throw a normal 404 page or a custom story not found template. If
``False``, the template `stories/story_removed.html` will be rendered.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'THROW_404': True
	}

.. _author_model:

AUTHOR_MODEL
============

Path to a Author model. This can be any valid model.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'AUTHOR_MODEL': u'auth.User'
	}

.. note::

    If you plan on using a custom author model, please see :ref:`author_guide`
    before you set this setting.

.. _author_model_limit_choices:

AUTHOR_MODEL_LIMIT_CHOICES
==========================

Used in conjuction with ``AUTHOR_MODEL``, on the ``limit_choices_to`` argument.

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'AUTHOR_MODEL_LIMIT_CHOICES': {'is_staff': True}
	}

.. _use_reversion:

USE_REVERSION
=============

.. versionchanged:: 1.0
   Default is now ``False``

This setting expects ``django-reversion`` to be installed and in your
``INSTALLED_APPS``

**Default:**

.. code-block:: python

	STORY_SETTINGS = {
	    'USE_REVERSION': False
	}

ORDERING
========

.. versionchanged:: 1.0
    This setting used to be called ``STORY_ORDERING``

The default ``ordering`` for stories

**Default:**

.. code-block:: python

    STORY_SETTINGS = {
        'ORDERING': ['-modified_data'],
    }


WIDGET
======

.. versionadded:: 1.0

Path of the widget module to use for ``story.body``

**Default:**

.. code-block:: python

    STORY_SETTINGS = {
        'WIDGET': None,
    }

WIDGET_ATTRS
============

.. versionadded:: 1.0

Dictionary of the attributes to supply the widget for ``story.body``. This
also includes suppling the default widget ``Textarea``

**Default:**

.. code-block:: python

    STORY_SETTINGS = {
        'WIDGET_ATTRS': None
    }

ADMIN_EXTRAS
============

.. versionadded:: 1.0

This is a dictionary of configurable admin attributes of the ``StoryAdmin``
class. Here are list of the configurable attributes.

* ``EXTRA_FIELDSETS`` - Allows for adding any extra fieldsets
* ``RAW_ID_FIELDS`` - A list/tuple of any fields you want act `raw_id`,
  default is ``()``
* ``FILTER_HORIZONTAL_FIELDS`` - A list/tuple of fields you want to be,
  added to ``FILTER_HORIZONTAL``, default is ``('authors',)``
* ``SEARCH_FIELDS`` - A list/tuple of the fields you want to be searchable,
  default is ``('headline',)``
* ``LIST_PER_PAGE`` - A integer of the number of stories per page,
  default is ``25``


The ``EXTRA_FIELDSETS`` is a tuple of any extra ``story`` admin fieldsets.
This setting is useful when external apps, such as ``tagging`` or
``categories``, add fields to ``stories``. Here is an example of the setting.

.. code-block:: python

    STORY_SETTINGS = {
        ...
        'ADMIN_EXTRAS': {
            'EXTRA_FIELDSETS' = (
                {
                    'name': 'Categories',
                    'fields': ('primary_category', 'categories')
                    'classes': (),
                    'description': None,
                    'position': None,
                },
                {
                    'name': 'Tagging',
                    'fields': ('tags',)
                    'classes': ('collapse',),
                    'position': 3,
            )
        }
        ...
    }

While ``name``, ``fields``, ``classes`` and ``description`` should be
`obvious <https://docs.djangoproject.com/en/1.4/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets>`_,
``position`` allows you to speicify the index where the fieldset will be
inserted. By default, these extra fieldsets will be appended.
