# coding: utf-8
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from adfav.models import Favorite


class FavoriteFilter(SimpleListFilter):

    title = _('Favorite')
    parameter_name = 'byfavorite'

    def lookups(self, request, model_admin):
        return (
            ('true', _('In favorite')),
            ('false', _('Outside favorite')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            model = queryset.model
            model_name = model._meta.module_name
            app_label = model._meta.app_label
            try:
                ctype_id = ContentType.objects.get(app_label=app_label, 
                                                    model=model_name).id
            except ContentType.DoesNotExist:
                pass
            else:
                qs_ids = [q.id for q in queryset]
                item_ids = Favorite.objects.filter(ctype_id=ctype_id, 
                                item__in=qs_ids, 
                                user_id=request.user.id).values_list('item', flat=True)
                if value == 'true':
                    queryset = queryset.filter(id__in=item_ids)
                elif value == 'false':
                    queryset = queryset.exclude(id__in=item_ids)
                else:
                    queryset = queryset.none()
        return queryset


def add_to_favorite(modeladmin, request, queryset):
    model = modeladmin.model
    model_name = model._meta.module_name
    app_label = model._meta.app_label
    try:
        ctype_id = ContentType.objects.get(app_label=app_label, 
                                            model=model_name).id
    except ContentType.DoesNotExist:
        pass
    else:
        qs_ids = [q.id for q in queryset]
        exist_ids = Favorite.objects.filter(user_id=request.user.id,
                                    ctype_id=ctype_id,
                                    item__in=qs_ids)
        queryset = queryset.exclude(id__in=exist_ids)
        for q in queryset:
            Favorite.objects.create(user_id=request.user.id, item=q.id, ctype_id=ctype_id)
add_to_favorite.short_description = _('Add to favorite')


def delete_from_favorite(modeladmin, request, queryset):
    model = modeladmin.model
    model_name = model._meta.module_name
    app_label = model._meta.app_label
    try:
        ctype_id = ContentType.objects.get(app_label=app_label, 
                                            model=model_name).id
    except ContentType.DoesNotExist:
        pass
    else:
        qs_ids = [q.id for q in queryset]
        Favorite.objects.filter(user_id=request.user.id,
                                ctype_id=ctype_id,
                                item__in=qs_ids).delete()
delete_from_favorite.short_description = _('Delete from favorite')
