"""hunting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# from vacancies.views import VacancyViewSet
from rest_framework import routers

from vacancies.views import SkillsViewSet

router = routers.SimpleRouter()
# router.register(r'vacancy', VacancyViewSet)
router.register(r'skill', SkillsViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # path('api/v1/', include(router.urls)), #  http://127.0.0.1:8000/api/v1/vacancy/
    # path('', include(router.urls)), # один вариант прописать роутеры(routers)

    path('vacancy/', include('vacancies.urls')),
    path('company/', include('companies.urls')),
]

urlpatterns += router.urls # второй вариант прописать роутеры(routers)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
