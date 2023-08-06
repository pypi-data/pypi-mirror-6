import unittest
import webtest


class AppEngineTest(unittest.TestCase):
    """
    Basic class from which all app engine test cases can inherit from.
    Handles setting up the testbed and provides utilities to log in
    users and run deferred tasks.
    """

    def setUp(self):
        from .testbed import FullTestBed
        self.testbed = FullTestBed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def loginUser(self, email='test@example.com', admin=False):
        self.testbed.login_user(email, admin)

    login_user = loginUser

    def runDeferredTasks(self, queue='default'):
        self.testbed.run_deferred_tasks(self, queue)

    run_deferred_tasks = runDeferredTasks


class AppEngineWebTest(AppEngineTest):
    """
    Provides a complete app engine testbed as well as a webtest instance
    available at ``self.testapp``. You can add routes using ``self.add_route``
    or add a ferris controller using ``self.add_controller``.
    """
    def setUp(self):
        from webapp2 import WSGIApplication
        super(AppEngineWebTest, self).setUp()
        app = WSGIApplication(debug=True, config={
            'webapp2_extras.sessions': {'secret_key': 'notasecret'}
        })
        self.testapp = webtest.TestApp(app)

    def add_controller(self, c):
        c._build_routes(self.testapp.app.router)

    addController = add_controller

    def add_route(self, r):
        self.testapp.app.router.add(r)

    addRoute = add_route


class FerrisAppTest(AppEngineTest):
    """
    Provides a complete App Engine test environment and also automatically routes
    all application and plugin handlers to ``testapp``.
    """
    def setUp(self):
        super(FerrisAppTest, self).setUp()

        import main
        reload(main)
        self.testapp = webtest.TestApp(main.main_app)
