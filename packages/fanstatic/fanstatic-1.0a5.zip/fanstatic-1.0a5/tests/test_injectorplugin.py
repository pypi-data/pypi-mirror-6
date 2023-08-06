import pytest

from fanstatic import Library, Resource, NeededResources
from fanstatic.injector import InjectorPlugin
from fanstatic.registry import InjectorRegistry
from fanstatic import make_injector
from fanstatic import compat
from fanstatic import ConfigurationError
from fanstatic.injector import TopBottomInjector


class TopInjector(InjectorPlugin):

    name = 'top'

    def __call__(self, html, needed):
        needed_html = self.make_inclusion(needed).render()
        return html.replace(
            compat.as_bytestring('<head>'),
            compat.as_bytestring('<head>%s' % needed_html), 1)

def test_injector_based_on_injectorplugin():
    foo = Library('foo', '')
    a = Resource(foo, 'a.css')
    b = Resource(foo, 'b.css', bottom=True)
    needed = NeededResources(resources=[a,b])

    inj = TopInjector({})

    html = b'<html><head></head><body></body></html>'

    assert inj(html, needed) == \
        compat.as_bytestring('''<html><head><link rel="stylesheet" type="text/css" href="/fanstatic/foo/a.css" />
<link rel="stylesheet" type="text/css" href="/fanstatic/foo/b.css" /></head><body></body></html>''')


class TestingRegistry(object):

    def __init__(self, request):
        self.request = request

    def add_injector(self, injector):
        return self._register_injector(InjectorRegistry, injector)

    def _register_injector(self, registry, injector):
        self.request.addfinalizer(
            lambda: registry.instance().pop(injector.name))
        registry.instance().add(injector)
        return injector


@pytest.fixture
def injectors(request):
    return TestingRegistry(request)


def test_injector_plugin_registered_by_name(injectors):
    with pytest.raises(KeyError):
        InjectorRegistry.instance()['top']

    injectors.add_injector(TopInjector)

    # After registering, no longer raise a key error.
    InjectorRegistry.instance()['top']


def test_wsgi_middleware_lookup_injector():
    injector_middleware = make_injector(None, {})
    # Default is the topbottom injector
    assert isinstance(injector_middleware.injector, TopBottomInjector)

    with pytest.raises(ConfigurationError):
        make_injector(None, {}, injector='foo')


def test_wsgi_middleware_lookup_injector_register(injectors):
    with pytest.raises(ConfigurationError):
        make_injector(None, {}, injector='top')

    injectors.add_injector(TopInjector)

    # After registering, no longer raise a Configuration Error.
    make_injector(None, {}, injector='top')
