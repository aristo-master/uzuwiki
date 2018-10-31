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

app_name = 'wikis.maintenances'


def get_urlpatterns():
    urlpatterns = [
        path('maintenance', views.WikiMaintenanceView.as_view(), name='index'),
    ]

    # 階層構造に対応する。param_count - 2 が上限
    param_count = hierarchy_count + 2

    for param in [
        {
            "name": "maintenance",
            "view": views.PageMaintenanceView.as_view()
        }
    ]:

        for num_total in range(1, param_count):
            str = param["name"] + "/"
            for num in range(0, num_total):
                str = str + '<str:page_name_{}>'.format(num)
                if num != num_total - 1:
                    str = str + '/'.format(num)

            urlpatterns.append(path(str, param["view"], name=param["name"]))

    return urlpatterns


urlpatterns = get_urlpatterns()
