from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^add/(?P<app_label>[a-z]+)/(?P<model_name>[a-z]+)/(?P<item_id>\d+)/$',
			'adfav.views.add_to_favorite'),
	url(r'^delete/(?P<app_label>[a-z]+)/(?P<model_name>[a-z]+)/(?P<item_id>\d+)/$',
			'adfav.views.delete_from_favorite'),

)
