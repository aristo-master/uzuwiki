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

app_name = 'wikis.pages'


def get_urlpatterns():
    urlpatterns = [
        path('', views.IndexView.as_view(), name='index'),
        path('create', views.CreateView.as_view(), name='create'),
        path('copy', views.CopyView.as_view(), name='copy'),
        path('list', views.ListView.as_view(), name='list'),
        path('updates', views.UpdatesView.as_view(), name='updates'),
        path('help', views.HelpView.as_view(), name='help'),
        path('sitemap.xml', views.sitemap, name='sitemap'),
    ]

    # 階層構造に対応する。param_count - 2 が上限
    param_count = hierarchy_count + 2

    for param in [
        {
            "name": "edit",
            "view": views.EditView.as_view()
        },
        {
            "name": "copy",
            "view": views.CopyView.as_view()
        },
    ]:

        for num_total in range(1, param_count):
            str = param["name"] + "/"
            for num in range(0, num_total):
                str = str + '<str:page_name_{}>'.format(num)
                if num != num_total - 1:
                    str = str + '/'.format(num)

            urlpatterns.append(path(str, param["view"], name=param["name"]))

    for num_total in range(1, param_count):
        str = ""
        for num in range(0, num_total):
            str = str + '<str:page_name_{}>'.format(num)
            if num != num_total - 1:
                str = str + '/'.format(num)

        urlpatterns.append(path(str, views.ShowView.as_view(), name="show"))

    return urlpatterns


urlpatterns = get_urlpatterns()
