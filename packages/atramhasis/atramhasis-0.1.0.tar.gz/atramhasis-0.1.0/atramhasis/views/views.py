from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from skosprovider.skos import Concept
from skosprovider.skos import Collection

from atramhasis.errors import SkosRegistryNotFoundException


@view_defaults(accept='text/html')
class AtramhasisView(object):
    '''
    This object groups HTML views part of the public user interface.
    '''

    def __init__(self, request):
        self.request = request
        if hasattr(request, 'skos_registry') and request.skos_registry is not None:
            self.skos_registry = self.request.skos_registry
        else:
            raise SkosRegistryNotFoundException()

    @view_config(route_name='home', renderer='atramhasis:templates/atramhasis.jinja2')
    def home_view(self):
        '''
        This view displays the homepage.

        :param request: A :class:`pyramid.request.Request`
        '''
        conceptschemes = [x.get_metadata() for x in self.skos_registry.get_providers()]
        return {'conceptschemes': conceptschemes}

    @view_config(route_name='concept', renderer='atramhasis:templates/concept.jinja2')
    def concept_view(self):
        '''
        This view displays the concept details

        :param request: A :class:`pyramid.request.Request`
        '''
        scheme_id = self.request.matchdict['scheme_id']
        c_id = self.request.matchdict['c_id']
        prov = self.request.skos_registry.get_provider(scheme_id)
        if prov:
            c = prov.get_by_id(c_id)
            if c:
                skostype = ""
                if isinstance(c, Concept):
                    skostype = "Concept"
                if isinstance(c, Collection):
                    skostype = "Collection"
                return {'concept': c, 'conceptType': skostype, 'scheme_id': scheme_id}
        return Response(content_type='text/plain', status_int=404)

    @view_config(route_name='search_result', renderer='atramhasis:templates/search_result.jinja2')
    def search_result(self):
        '''
        This view displays the search results

        :param request: A :class:`pyramid.request.Request`
        '''
        label = None
        scheme_id = self.request.matchdict['scheme_id']
        if 'label' in self.request.params:
            label = self.request.params.getone('label')
            print('search for: ' + label)
        provider = self.skos_registry.get_provider(scheme_id)
        if provider:
            if label is not None:
                concepts = provider.find({'label': label})
            else:
                concepts = provider.get_all()
            return {'concepts': concepts, 'scheme_id': scheme_id}
        return Response(content_type='text/plain', status_int=404)

    @view_config(route_name='locale')
    def set_locale_cookie(self):
        '''
        This view will set a language cookie

        :param request: A :class:`pyramid.request.Request`
        '''
        if self.request.GET['language']:
            language = self.request.GET['language']
            response = HTTPFound(location=self.request.environ['HTTP_REFERER'])
            response.set_cookie('_LOCALE_',
                                value=language,
                                max_age=31536000)  # max_age = year
        return response