"""lpc_g2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url, include
from tastypie.api import Api
from django.contrib import admin
from evento.api.resources import *

from evento.views import *

v1_api = Api(api_name='v1')
#v1_api.register(UserResource())
v1_api.register(EventoResource())
v1_api.register(PessoaResource())
v1_api.register(PessoaFisicaResource())
#v1_api.register(EventoCientificoResource())
#v1_api.register(AutorResource())
#v1_api.register(AvaliadorResource())
#v1_api.register(ArtigoCientificoResource())
#v1_api.register(ArtigoAutorResource())
#v1_api.register(AvaliacaoArtigoResource())
#v1_api.register(TipoInscricaoResource())
#v1_api.register(InscricoesResource())


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls)),
]
