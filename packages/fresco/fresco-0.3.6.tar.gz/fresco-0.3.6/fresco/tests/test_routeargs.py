from mock import Mock

from fresco import Route, GET, FrescoApp
from fresco import routeargs


class TestRouteArg(object):

    def test_routekwarg_configured(self):

        A = routeargs.RouteArg()
        route = Route('/', GET, lambda r: None, x=A)
        assert A.route is route
        assert A.name is 'x'

    def test_routekwarg_value_passed(self):

        view = Mock()
        routekwarg = Mock(spec=routeargs.RouteArg)
        routekwarg.return_value = 'xyzzy'

        app = FrescoApp()
        app.route('/', GET, view, x=routekwarg)
        with app.requestcontext('/') as c:
            app.view()
            routekwarg.assert_called_with(c.request)
            view.assert_called_with(x='xyzzy')

    def test_queryarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.QueryArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_formarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg())
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_sessionarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.SessionArg())
        with app.requestcontext('/?x=foo') as c:
            c.request.environ[c.request.SESSION_ENV_KEY] = {'x': 'foo'}
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.CookieArg())
        with app.requestcontext('/', HTTP_COOKIE='x=foo'):
            app.view()
            view.assert_called_with(x='foo')

    def test_cookiearg_listvalue_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.CookieArg([str]))
        with app.requestcontext('/', HTTP_COOKIE='x=foo;x=bar'):
            app.view()
            view.assert_called_with(x=['foo', 'bar'])

    def test_requestarg_value_converted(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(float))
        with app.requestcontext('/?x=0'):
            app.view()
            view.assert_called_with(x=0.0)

    def test_requestarg_default_value(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg(default='d'))
        with app.requestcontext('/'):
            app.view()
            view.assert_called_with(x='d')

    def test_access_to_missing_requestarg_returns_badrequest(self):
        def view(x):
            x == 0
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormArg())
        with app.requestcontext('/'):
            assert 'Bad Request' in app.view().status

    def test_routeargs_work_as_positional_arguments(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, args=[routeargs.FormArg(key='x')])
        with app.requestcontext('/?x=foo'):
            app.view()
            view.assert_called_with('foo')


class TestRequestObject(object):

    def test_it_passes_the_request(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.RequestObject())
        with app.requestcontext('/') as c:
            app.view()
            x = view.call_args[1]['x']
            assert x is c.request


class TestFormData(object):

    def test_it_passes_the_form_dict(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=routeargs.FormData())
        with app.requestcontext('/') as c:
            app.view()
            x = view.call_args[1]['x']
            assert x is c.request.form
