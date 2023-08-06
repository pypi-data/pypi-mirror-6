# -*- coding: utf-8 -*-
"""Services expose diecutter API."""
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import cornice
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotImplemented, HTTPNotAcceptable

import diecutter
import diecutter.validators
import diecutter.utils
from diecutter.writers import (zip_directory_response,
                               file_response,
                               targz_directory_response)


class Service(object):
    """Base class for diecutter services."""
    def hello(self, request):
        """Returns Hello and API version in JSON."""
        return OrderedDict((
            ('diecutter', 'Hello'),
            ('version', diecutter.__version__),
        ))

    def get(self, request):
        raise HTTPNotImplemented()

    def post(self, request):
        raise HTTPNotImplemented()

    def put(self, request):
        raise HTTPNotImplemented()

    def get_resource(self, request):
        """Return the resource object (instance) matching request."""
        raise NotImplementedError()

    def get_engine(self, request):
        """Return configured template engine to render templates."""
        settings = request.registry.settings
        config = Configurator(settings)
        engine_factory_path = settings['diecutter.template_engine']
        engine_factory = config.maybe_dotted(engine_factory_path)
        engine = engine_factory()
        return engine

    def get_filename_engine(self, request):
        """Return configured template engine to render filenames.

        This is not used for dynamic trees.

        """
        settings = request.registry.settings
        config = Configurator(settings)
        engine_factory_path = settings['diecutter.filename_template_engine']
        engine_factory = config.maybe_dotted(engine_factory_path)
        engine = engine_factory()
        return engine

    def get_writers(self, request, resource, context):
        """Return iterable of writers."""
        if resource.is_file:
            return [file_response]
        else:
            accepted_mime_types = diecutter.utils.accepted_types(request)
            # Reference.
            mime_map = {'application/zip': [zip_directory_response],
                        'application/gzip': [targz_directory_response],
                        }
            # Aliases.
            mime_map['application/x-gzip'] = mime_map['application/gzip']
            # Fallback.
            settings = request.registry.settings
            try:
                default_type = settings['diecutter.default_archive_type']
            except KeyError:
                default_type = 'application/gzip'
            if default_type not in mime_map.keys():
                raise ConfigurationError(
                    'Cannot use "{type}" as "default_archive_type". Supported '
                    'types are: {supported}'.format(
                        type=default_type,
                        supported=','.join(mime_map.keys())))
            mime_map['*/*'] = mime_map[default_type]
            for accepted_mime_type in accepted_mime_types:
                try:
                    return mime_map[accepted_mime_type]
                except KeyError:
                    pass
            raise HTTPNotAcceptable('Supported mime types: %s'
                                    % ', '.join(sorted(mime_map.keys())))

    def get_dispatcher(self, request, resource, context, writers):
        """Return simple dispatcher (later, would read configuration)."""
        return diecutter.utils.dispatchers.FirstResultDispatcher(writers)

    def is_readonly(self, request):
        """Return "readonly" flag status (boolean) for request.

        As an example, PUT operations should be forbidden if readonly flag is
        On.

        """
        readonly = request.registry.settings.get('diecutter.readonly', False)
        return diecutter.utils.to_boolean(readonly)


def register_service(config, name, service, path):
    """Register a diecutter service in Pyramid routing."""
    hello = cornice.Service(name='{name}_hello'.format(name=name),
                            path=path,
                            description="The template API",
                            cors_origins=('*',))
    template = cornice.Service(
        name='{name}_template'.format(name=name),
        path='%s{template_path:.+}' % path,
        description="Return the template render or raw")
    hello.add_view('GET', service.hello)
    template.add_view('PUT', service.put,
                      validators=(diecutter.validators.token_validator,))
    template.add_view('GET', service.get)
    template.add_view('POST', service.post)
    cornice.register_service_views(config, hello)
    cornice.register_service_views(config, template)
