"""heibon_django URL Configuration

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

from django.urls import path
from django.conf import settings
from .utils import setting_name

from . import views

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

app_name = 'accounts'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/<str:social_name>', views.auth, name='begin'),
    path('complete/<str:social_name>', views.CompleteView.as_view(), name='complete'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('info', views.InfoView.as_view(), name='info'),
]
