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
from uzuwiki.settings import hierarchy_count
from . import views

app_name = 'webapis'

urlpatterns = [
    path('md_to_html', views.md_to_html, name='md_to_html'),
    path('get_side_bar', views.get_side_bar, name='get_side_bar'),
    path('get_latest_update', views.get_latest_update, name='get_latest_update'),
]
