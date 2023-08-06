# coding: utf-8
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from adfav.models import Favorite
from adfav.fake_field import favorite_field
from adfav.utils import FavoriteFilter, add_to_favorite, delete_from_favorite


class FavoriteAdmin(admin.ModelAdmin):

    # list_filter = (FavoriteFilter,)
    # actions = [add_to_favorite, delete_from_favorite]

    def get_list_display(self, request):
        return list(self.list_display) + [favorite_field]

    def queryset(self, request):
        queryset = super(FavoriteAdmin, self).queryset(request)
        model = self.model
        model_name = model._meta.module_name
        app_label = model._meta.app_label
        qs_ids = [i.id for i in queryset]
        try:
            ctype_id = ContentType.objects.get(app_label=app_label, 
                                                model=model_name).id
        except ContentType.DoesNotExist:
            pass
        else:
            favorites = Favorite.objects.filter(user_id=request.user.id, 
                                ctype_id=ctype_id, 
                                item__in=qs_ids).values_list('item', flat=True)
            self.model.items_list = favorites
            self.model.next = request.get_full_path()
        return queryset