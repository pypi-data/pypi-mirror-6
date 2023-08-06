# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings

from adfav.models import Favorite

ADFAV_ADD_LABEL = getattr(settings, 'ADFAV_ADD_LABEL', _('Add'))
ADFAV_DELETE_LABEL = getattr(settings, 'ADFAV_DELETE_LABEL', _('Delete'))
ADFAV_HEADER_LABEL = getattr(settings, 'ADFAV_HEADER_LABEL', _('Favorite'))


def favorite_field(self):
	model = self.__class__
	app_label = model._meta.app_label
	model_name = model._meta.module_name
	favorites = getattr(model, 'items_list', [])
	if self.id not in favorites:
		url = reverse('adfav.views.add_to_favorite', kwargs={
				'app_label': app_label,
				'model_name': model_name,
				'item_id': self.id,
			})
		result = '<a href="%s?next=%s">%s</a>' % (url, getattr(model, 'next', ''), ADFAV_ADD_LABEL)
	else:
		url = reverse('adfav.views.delete_from_favorite', kwargs={
				'app_label': app_label,
				'model_name': model_name,
				'item_id': self.id,
			})
		result = '<a href="%s?next=%s">%s</a>' % (url, getattr(model, 'next', ''), ADFAV_DELETE_LABEL)
	return result
favorite_field.short_description = ADFAV_HEADER_LABEL
favorite_field.allow_tags = True
