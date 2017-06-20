from django.utils.baseconv import base64
from tastypie.resources import ModelResource
from tastypie import fields, utils
from evento.models import *
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.authentication import *
from django.contrib.auth.models import User
from django.http.request import *

class PessoaResource(ModelResource):
    class Meta:
        queryset = Pessoa.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            "nome": ('exact', 'startswith',)
        }

class PessoaFisicaResource(ModelResource):
    class Meta:
        queryset = PessoaFisica.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            "cpf": ('exact', 'startswith',)
        }

class AutorResource(ModelResource):
    class Meta:
        queryset = Autor.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            "curriculo": ('exact', 'startswith',)
        }

class AvaliadorResource(ModelResource):
    class Meta:
        queryset = Avaliador.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            "curriculo": ('exact', 'startswith',)
        }

class EventoResource(ModelResource):
    realizador = fields.ToOneField(PessoaFisicaResource, 'realizador')
    def obj_get_list(self, bundle, **kwargs):
        if bundle.request.user.is_superuser or Autor.objects.filter(usuario=bundle.request.user):
            return Evento.objects.all()
        else:
            raise Unauthorized('Você não tem permissão')

    def obj_create(self, bundle, **kwargs):
        if bundle.request.user.is_superuser:
            r = bundle.data['realizador'].split("/")[-2]
            evento = Evento()
            evento.nome = bundle.data["nome"]
            evento.sigla = bundle.data["sigla"]
            evento.dataEHoraDeInicio = bundle.data["dataEHoraDeInicio"]
            evento.realizador = PessoaFisica.objects.get(pk=r)
            evento.save()

            bundle.obj = evento
            return bundle
        else:
            raise Unauthorized("Você não possui permissão para incluir.")

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        pk = int(kwargs['pk'])
        if bundle.request.user.is_superuser:
            r = bundle.data['realizador'].split("/")[-2]
            evento = Evento.objects.get(pk=pk)
            evento.nome = bundle.data["nome"]
            evento.sigla = bundle.data["sigla"]
            evento.dataEHoraDeInicio = bundle.data["dataEHoraDeInicio"]
            evento.realizador = PessoaFisica.objects.get(pk=r)
            evento.save()

            bundle.obj = evento
            return bundle
        else:
            raise Unauthorized("Você não possui permissão para incluir.")

    def obj_delete(self, bundle, **kwargs):
        pk = int(kwargs['pk'])
        insc = Inscricoes.objects.filter(evento_id=pk)
        artigos = ArtigoCientifico.objects.filter(evento_id=pk)
        if bundle.request.user.is_superuser:
            if insc.exists() and artigos.exists():
                raise Unauthorized("Você não tem autorização para excluir")
            else:
                evento = Evento.objects.get(pk=pk)
                evento.delete()

    def obj_delete_list(self, bundle, **kwargs):
        raise Unauthorized("Você não pode excluir uma lista")

    class Meta:
        queryset = Evento.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        # authorization = Authorization()
        authentication = ApiKeyAuthentication()
        filtering = {
            "nome": ('exact', 'startswith',)
        }

class ArtigoCientificoResource(ModelResource):
    def obj_get_list(self, bundle, **kwargs):
        usuario = bundle.request.user
        return ArtigoCientifico.objects.filter(autor=usuario)

    def obj_create(self, bundle, **kwargs):
        if Autor.objects.filter(usuario=bundle.request.user):
            e = bundle.data['evento'].split("/")[-2]
            artigo = ArtigoCientifico()
            artigo.titulo = bundle.data["titulo"]
            artigo.resumo = bundle.data["resumo"]
            artigo.palavras_chave = bundle.data["palavras_chave"]
            artigo.evento = EventoCientifico.objects.get(pk=e)
            artigo.save()

            bundle.obj = artigo
            return bundle
        else:
            raise Unauthorized("Você não possui permissão para incluir.")

    def obj_delete(self, bundle, **kwargs):
        pk = int(kwargs['pk'])
        avaliacao = AvaliacaoArtigo.objects.filter(artigo_id=pk)
        if Autor.objects.filter(usuario=bundle.request.user):
            if avaliacao.exists():
                raise Unauthorized("Você não tem autorização para excluir")
            else:
                artigo = ArtigoCientifico.objects.get(pk=pk)
                artigo.delete()

    def obj_delete_list(self, bundle, **kwargs):
        raise Unauthorized("Você não pode excluir uma lista")

    class Meta:
        queryset = ArtigoCientifico.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authentication = ApiKeyAuthentication()
        filtering = {
            "titulo": ('exact', 'startswith',)
        }

class ArtigoAutorResource(ModelResource):
    artigoCientifico = fields.ToOneField(ArtigoCientificoResource, 'artigoCientifico')
    autor = fields.ToOneField(AutorResource, 'autor')

    def obj_get_list(self, bundle, **kwargs):
        if Autor.objects.filter(usuario=bundle.request.user):
            return ArtigoAutor.objects.all()

    def obj_delete_list(self, bundle, **kwargs):
        raise Unauthorized("Você não pode excluir uma lista")

    class Meta:
        queryset = ArtigoAutor.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authentication = ApiKeyAuthentication()

class CriterioAvaliacaoResource(ModelResource):
    class Meta:
        queryset = CriterioAvaliacao.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            "nome": ('exact', 'startswith',)
        }

class AvaliacaoArtigoResource(ModelResource):
    avaliador = fields.ToOneField(AvaliadorResource, 'avaliador')
    artigo = fields.ToOneField(ArtigoCientificoResource, 'artigo')
    criterio = fields.ToOneField(CriterioAvaliacaoResource, 'criterio')

    def obj_create(self, bundle, **kwargs):
        if Avaliador.objects.filter(usuario=bundle.request.user):
            ava = bundle.data['avaliador'].split("/")[-2]
            art = bundle.data['artigo'].split("/")[-2]
            cri = bundle.data['criterio'].split("/")[-2]
            avaliacao = AvaliacaoArtigo()
            avaliacao.avaliador = Avaliador.objects.get(pk=ava)
            avaliacao.artigo = ArtigoCientifico.objects.get(pk=art)
            avaliacao.criterio = CriterioAvaliacao.objects.get(pk=cri)
            avaliacao.nota = bundle.data["nota"]
            avaliacao.save()

            bundle.obj = avaliacao
            return bundle
        else:
            raise Unauthorized("Você não possui permissão para incluir.")

    def obj_delete(self, bundle, **kwargs):
        pk = int(kwargs['pk'])
        if Avaliador.objects.filter(usuario=bundle.request.user):
            avaliacao = AvaliacaoArtigo.objects.get(pk=pk)
            avaliacao.delete()
        else:
            raise Unauthorized("Você não tem autorização para excluir")

    def obj_delete_list(self, bundle, **kwargs):
        raise Unauthorized("Você não pode excluir uma lista")


    class Meta:
        queryset = AvaliacaoArtigo.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authentication = ApiKeyAuthentication()

