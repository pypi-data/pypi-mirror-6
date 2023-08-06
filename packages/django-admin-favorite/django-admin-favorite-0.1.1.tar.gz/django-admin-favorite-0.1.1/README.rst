=====
django-admin-favorite
=====

adfav is simple application for adding any model instances to favorite in admin change list. 
And after then you can get all you favorite items at one click.

Quick start
-----------

1. Add "adfav" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'adfav',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^adfav/', include('adfav.urls')),

3. Run sync command::
    
    python manage.py syncdb

3. Inherit adfav admin class in you admin.py, like this::

    # admin.py
    from django.contrib import admin
    from myapp.models import MyModel
    from adfav.admin import FavoriteAdmin

    class MyModelAdmin(FavoriteAdmin):
        ...
    admin.site.register(MyModel, MyModelAdmin)

4. Also, you can get built-in filter by favorite-mark and/or built-in actions (add/remove from favorite)::

    # admin.py
    from django.contrib import admin
    from myapp.models import MyModel
    from adfav.admin import FavoriteAdmin
    from adfav.utils import FavoriteFilter, add_to_favorite, delete_from_favorite

    class MyModelAdmin(FavoriteAdmin):
        list_filter = (FavoriteFilter,)
        actions = (add_to_favorite, delete_from_favorite)
    admin.site.register(MyModel, MyModelAdmin)


Settings
--------

You can define labes, that displayed in you admin model::

    ADFAV_ADD_LABEL = 'Add to favorite'         # default: 'Add'
    ADFAV_DELETE_LABEL = 'Delete from favorite' # default: 'Delete'
    ADFAV_HEADER_LABEL = 'My favorite list'     # default: 'Favorite'


questions: support@vmn.su