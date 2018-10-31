"""uzuwiki URL Configuration

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
from django.urls import include, path
from django.http import HttpResponseBadRequest


def dummy(request):
    return HttpResponseBadRequest("")


urlpatterns = [
    path('', include('roots.urls')),
    path('favicon.ico/', dummy, name='favicon_block'),
    path('accounts/', include('accounts.urls')),
    path('admins/', include('admins.urls')),
    path('webapi/', include('webapis.urls')),
    path('<str:wiki_id>/', include('wikis.urls')),
]
