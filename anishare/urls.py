"""anishare URL Configuration

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
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.decorators.cache import never_cache

from animals import urls
import animals

urlpatterns = [
#    path('', animals.views.AnimalIndexView.as_view(), name='root'),
    path('', animals.views.animal_list, name='animal-list'),
    path('animals/', include('animals.urls', namespace='animals-index')),
    path('organs/', animals.views.organ_list, name='organs'),
    path('animals/claim', animals.views.AnimalClaimView, name='claim_animals'),
    #path('animals/fishpeople', animals.views.tickatlabpersonlist, name='view_tickatlabperson'),
    #path('animals/fishfromtickatlab', animals.views.tickatlabfishlist, name='view_tickatlabfish'),
    #path('animals/importfish', animals.views.importfish_view, name='importfish'),
    #path('animals/importfishtoanishare', animals.views.importfishtoanishare, name='importfishtoanishare'),
    path('organs/claim/<int:primary_key>', animals.views.claim_organ, name='claim_organ'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    #re_path(r'^jet/', jet.urls, name='jet'),  # Django JET URLS
    path('admin/', admin.site.urls),
    path('macros/', animals.views.macros, name='macro'),
    path('changehistory/', animals.views.change_history, name='change'),
    path('changehistory/feed', never_cache(animals.views.LatestChangesFeed()), name='version-feed'),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
