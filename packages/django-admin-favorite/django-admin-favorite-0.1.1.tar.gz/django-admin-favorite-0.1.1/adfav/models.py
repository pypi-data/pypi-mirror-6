# coding: utf-8
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models


class Favorite(models.Model):

	class Meta:
		unique_together = ('user', 'ctype', 'item')

	user = models.ForeignKey(User, related_name='user_favorites')
	ctype = models.ForeignKey(ContentType, related_name='ctype_favorite')
	item = models.PositiveIntegerField()
