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

from . import views

app_name = 'admins'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('google_credentials', views.GoogleCredentialsView.as_view(), name='google_credentials'),
    path('google_credentials_do', views.GoogleCredentialsDoView.as_view(), name='google_credentials_do'),
    path('google_credentials_complete', views.GoogleCredentialsCompleteView.as_view(), name='google_credentials_complete'),
]
