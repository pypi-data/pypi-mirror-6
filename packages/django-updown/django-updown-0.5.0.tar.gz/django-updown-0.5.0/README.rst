=============
django-updown
=============

.. image:: https://secure.travis-ci.org/weluse/django-updown.png?branch=master
    :alt: Travis CI build status
    :target: http://travis-ci.org/weluse/django-updown

``django-updown`` is a simple Django application for adding youtube like up and down voting.

---------
Changelog
---------

**0.5**:

- Fixed DateTimeField RuntimeWarning (thanks to `yurtaev
  <https://github.com/yurtaev>`_)
- Tests are using Django 1.4.10 now

**0.4**:

- Usage of ``AUTH_USER_MODEL`` instead of ``auth.models.User``
  (thanks to `timbutler <https://github.com/timbutler>`_)

**0.3**:

- Removed south as dependency
- Small cleanups (thanks to `gwrtheyrn <https://github.com/gwrtheyrn>`_)

**0.2**:

- Updated related_name to avoid namespace clashes.
- Added south as dependency

-----
Usage
-----
Add ``"updown"`` to your ``INSTALLED_APPS`` then just add a ``RatingField`` to
your existing model and go::

    from django.db import models
    from updown.fields import RatingField

    class Video(models.Model):
        # ...other fields...
        rating = RatingField()

You can also allow the user to change his vote::

    class Video(models.Model):
        # ...other fields...
        rating = RatingField(can_change_vote=True)

Now you can write your own view to submit ratings or use the predefinded::

    from updown.views import AddRatingFromModel

    urlpatterns = patterns("",
        url(r"^(?P<object_id>\d+)/rate/(?P<score>[\d\-]+)$", AddRatingFromModel(), {
            'app_label': 'video',
            'model': 'Video',
            'field_name': 'rating',
        }, name="video_rating"),
    )

To submit a vote just go to ``video/<id>/rate/(1|-1)``. If you allowed users to
change they're vote, they can do it with the same url.

If you're using Django version prior to 1.5, you have to add
``AUTH_USER_MODEL = 'auth.User'`` to your settings.

----------------
Troubleshooting
----------------
If you previously used this app you may get to a point where migrations are
failing.
Try::

    ./manage.py migrate updown --fake 0001

to skip the initial migration. After this apply the migrations again::

    ./manage.py migrate updown

------
Thanks
------
Thanks a lot to ``django-ratings`` for the inspiring code
