"""TeacherRating URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from TeacherRating import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/profile/',
        TemplateView.as_view(template_name='registration/profile.html'),
        name='profile'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^check_captcha$', views.check_captcha, name='check_captcha'),
    url(r'^panel/', include(('panel.urls', 'panel'), namespace='panel')),
    url(r'^rating/', include(('rating.urls', 'rating'), namespace='rating')),
    url(r'^questionnaire/', include(('questionnaire.urls', 'questionnaire'), namespace='questionnaire')),
    path('admin/', admin.site.urls),
]
