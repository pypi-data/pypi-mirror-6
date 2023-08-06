# coding: utf-8
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from adfav.models import Favorite


def add_to_favorite(request, app_label, model_name, item_id):
    try:
        item_id = int(item_id)
    except ValueError:
        pass
    else:
        try:
            ctype_id = ContentType.objects.get(app_label=app_label, 
                                                model=model_name).id
        except ContentType.DoesNotExist:
            pass
        else:
            favorites = Favorite.objects.filter(user_id=request.user.id, 
                                                ctype_id=ctype_id, 
                                                item=item_id)
            if not favorites:
                Favorite.objects.create(user_id=request.user.id,
                                        ctype_id=ctype_id,
                                        item=item_id)
    next = request.GET.get('next', '') or ''
    if not next:
        next = reverse('admin:index')
    return redirect(next)


def delete_from_favorite(request, app_label, model_name, item_id):
    try:
        item_id = int(item_id)
    except ValueError:
        pass
    else:
        try:
            ctype_id = ContentType.objects.get(app_label=app_label, 
                                                model=model_name).id
        except ContentType.DoesNotExist:
            pass
        else:
            Favorite.objects.filter(user_id=request.user.id, 
                                    ctype_id=ctype_id, 
                                    item=item_id).delete()
    next = request.GET.get('next', '') or ''
    if not next:
        next = reverse('admin:index')
    return redirect(next)
