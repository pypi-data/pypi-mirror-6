from pyramid.config import Configurator
from pyramid.response import Response
from pyramid_facebook.canvas import facebook_canvas



def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include(__name__)
    return config.make_wsgi_app()


def includeme(config):
    # XXX bug: when including only canvas, we have to specify route_prefix :-(
    config.include('pyramid_facebook.canvas',
                   route_prefix=config.registry.settings['facebook.namespace'])
    config.scan()


@facebook_canvas()
def canvas(request):
    return Response('Hello World')