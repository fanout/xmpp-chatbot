from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^xmpp/(?P<to>.*)$', views.xmpp),
]
