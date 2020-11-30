from django.conf.urls import url


from . import views # import views so we can use them in urls.

app_name = 'biblio'

urlpatterns = [
    url(r'^board/', views.board, name='board'),
]