from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views
from accounts.views import (login_view, register_view, logout_view,add_review)
from django.conf import settings
from django.conf.urls.static import static

app_name = 'movies'

urlpatterns = [
                  path('home', views.post_list, name='home'),
                  path('loginn', login_view, name='login'),
                  path('logout', logout_view, name='logout'),
                  path('register', register_view, name='register'),
                  path('recommendation', views.recommendation, name='recommendation'),
                  path('detail/<int:id>', views.detail, name='detail'),
                  path('addreview/<int:id>',add_review,name="add_review"),
                  path('search',views.search,name="search"),
                  path('editreview/<int:review_id>',views.edit_review,name="edit_review"),
                  path('deletereview/<int:review_id>',views.delete_review,name="delete_review"),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

