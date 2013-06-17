from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
from tvshowshack.models import get_root
import deform
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pkg_resources import resource_filename
from pyramid.threadlocal import get_current_request
from translationstring import TranslationStringFactory
from pyramid.i18n import get_localizer
from urlparse import urlparse
import pymongo

class PyramidTranslator(object):

    def __init__(self, domain='deform'):
        self.domain = domain

    def translate(self, term):

        if not hasattr(term, 'interpolate'): # not a translation string
            term = TranslationStringFactory(self.domain)(term)
        return get_localizer(get_current_request()).translate(term)

    def pluralize(self, singular, plural, n):
        localizer = get_localizer(get_current_request())
        return localizer.pluralize(singular, plural, n)


    def gettext(self, message):
        return self.translate(message)

    def ngettext(self, singular, plural, n):
        return self.pluralize(singular, plural, n)

class jinja2_renderer_factory(object):
    def __init__(self, search_paths=(), default_templates='tvshowshack:bootstrap_templates',
            translator=None, extensions=[]):

        if 'jinja2.ext.i18n' not in extensions:
           extensions.append('jinja2.ext.i18n')

        self.env = Environment(extensions=extensions)
        self.env.loader = FileSystemLoader(())

        for path in search_paths:
            self.add_search_path(path)

        if translator == None:
            translator = DummyTranslator

        self.env.install_gettext_callables(translator.gettext, translator.ngettext)

        self.add_search_path(default_templates)

    def add_search_path(self, path):
        self.env.loader.searchpath.append(resource_filename(*(path.split(':'))))

    def add_filter(self, name, func):
        self.env.filters[name] = func

    def __call__(self, tname, **kw):
        if not '.jinja2' in tname:
            tname += '.jinja2'

        template = self.env.get_template(tname)
        return template.render(**kw)


def includeme(config):
    settings = config.registry.settings
    domain = settings.get('deform_jinja2.i18n.domain', 'deform')
    search_path = settings.get('deform_jinja2.template_search_path', '').strip()
    renderer = jinja2_renderer_factory(search_paths=search_path.split(), 
            translator=PyramidTranslator(domain=domain))
    deform.Form.set_default_renderer(renderer)


    def add_filter(config, name, func):
        renderer.add_filter(name, func)

    config.add_directive('add_jinja2_filter', add_filter)

    config.registry['deform_jinja2_renderer'] = renderer

def main(global_config, **settings):
		""" This function returns a WSGI application.
		It is usually called by the PasteDeploy framework during 
		``paster serve``.
		"""
		settings = dict(settings)
		settings.setdefault('jinja2.i18n.domain', 'tvshowshack')
		config = Configurator(root_factory=get_root, settings=settings)
		config.add_static_view('static', 'static', cache_max_age=3600)
		config.add_translation_dirs('locale/')
		config.scan('tvshowshack')
		config.add_route('home', '/')
		config.add_route('signup', '/signup')
		db_url = urlparse(settings['mongo_uri'])
		config.registry.db = pymongo.Connection(
											host=db_url.hostname,
											port=db_url.port,
											)
		includeme(config)
		
		def add_db(request):
			db = config.registry.db[db_url.path[1:]]
			if db_url.username and db_url.password:
				db.authenticate(db_url.username, db_url.password)
			return db
           
		config.add_request_method(add_db, 'db', reify=True)

		return config.make_wsgi_app()
	

