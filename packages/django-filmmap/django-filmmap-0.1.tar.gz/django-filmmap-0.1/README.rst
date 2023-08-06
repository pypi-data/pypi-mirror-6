=======
FilmMap
=======

FilmMap is an API to find movies that are playing in the San Francisco area. Feel free to fork the repository and
use it for your own data sets!

Quick start
-----------


1. Add "filmmap" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'filmmap',
      )

2. Include the filmmap URLconfs in your project urls.py like this::

    urlpatterns = patterns('',
        url(r'^', include('filmmap.urls', namespace='filmmap')),
        url(r'^admin/', include(admin.site.urls)),
    )

3. Run ``python manage.py syncdb`` to create the filmmap models.

4. Run ``python manage.py update_films https://data.sfgov.org/resource/yitu-d5am.json`` to update the films database.

5. Visit http://127.0.0.1:8000/filmmap/ to run the application!

6. Feel free to fork the repository_ and create an API for your own data sets. Modify the api view in `views.py`, the
   the admin comment `update_films.py`, and the models in `models.py` to reflect your particular data set. 

.. _repository: http://github.com/Risto-Stevcev/django-filmmap
