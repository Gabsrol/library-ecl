from django.conf.urls import url


from . import views # import views so we can use them in urls.

app_name = 'biblio'

urlpatterns = [
    url(r'^board/', views.board, name='board'),
    url(r'^booking/(?P<reference_id>[0-9]+)/', views.booking, name='booking'),
    url(r'^booking/no_subscription/', views.no_subscription, name='no_subscription'),
    url(r'^subscribe/', views.subscribe, name='subscribe'),
]