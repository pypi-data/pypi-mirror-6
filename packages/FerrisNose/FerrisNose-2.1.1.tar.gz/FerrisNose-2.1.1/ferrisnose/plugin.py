import logging
import os
import sys

from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.ferrisnose')


class FerrisNose(Plugin):
    name = 'ferris'

    def options(self, parser, env=os.environ):
        super(FerrisNose, self).options(parser, env=env)

        parser.add_option(
            '--gae-sdk-path', default=env.get('APPENGINE_SDK_PATH', '/usr/local/google_appengine'),
            dest='gae_sdk_path',
            help='Set the path to the directory of the App Engine SDK installation (you can also use the APPENGINE_SDK_PATH environment variable)')

    def configure(self, options, conf):
        super(FerrisNose, self).configure(options, conf)

        if not self.enabled:
            return

        if not conf.testNames:
            log.warning('No test paths specified assuming app/tests')
            conf.testNames.append('app/tests')

        self.gae_path = options.gae_sdk_path

        self._check_path()
        self._setup_path()
        self._setup_testbed()
        self._setup_logging()

    def _check_path(self):
        wd = os.getcwd()
        if not os.path.exists(os.path.join(wd, 'app.yaml')):
            raise ValueError('No app.yaml found. Ferrisnose must be run from the root of your application.')

    def _setup_path(self):
        # Load the app engine path into sys
        sys.path.append(self.gae_path)

        # store the current path
        current_path = sys.path[:]

        # Try to import the app server
        try:
            import dev_appserver
        except ImportError:
            raise ValueError("Could not locate the App Engine SDK. Please provide the SDK path using the --gae-sdk-path argument or set the APPENGINE_SDK_PATH environment variable.")

        # make appengine load its libraries
        dev_appserver.fix_sys_path()

        # Reload the google module
        if 'google' in sys.modules:
            import google
            reload(google)

        # Restore the path and add the current directory to the path
        sys.path.extend(current_path)
        sys.path.append(os.getcwd())

    def _setup_testbed(self):
        # Activate a testbed during test discovery
        from .testbed import SimpleTestBed
        self.testbed = SimpleTestBed()
        self.testbed.activate()

    def _setup_logging(self):
        # Remove agressive logging
        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.INFO)
        for handler in rootLogger.handlers:
            if isinstance(handler, logging.StreamHandler):
                rootLogger.removeHandler(handler)

    def beforeTest(self, test):
        # Turn off the internal testbed before running a test.
        self.testbed.deactivate()
