from django.conf.urls import url

# from TeacherRating import views
from rating import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]