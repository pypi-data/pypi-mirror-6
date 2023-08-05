import logging
import os
import sys
import re

from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.nosegunit')


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

        self.gae_path = options.gae_sdk_path

        self._setup_path()
        self._setup_testbed()

    def _setup_path(self):
        # Load the app engine path into sys
        sys.path.append(self.gae_path)

        # store the current path
        current_path = sys.path[:]

        # make appengine load its libraries
        from dev_appserver import fix_sys_path
        fix_sys_path()

        # Fix library versions
        sys.path = [re.sub('webob_0_9', 'webob_1_1_1', x) for x in sys.path]

        # Reload the google module
        if 'google' in sys.modules:
            import google
            reload(google)

        # Restore the path and add the current directory to the path
        sys.path.extend(current_path)
        sys.path.append(os.getcwd())

    def _setup_testbed(self):
        # Activate a testbed so that httplib2 always knows that it's in app engine
        from google.appengine.ext import testbed
        from google.appengine.datastore import datastore_stub_util
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)
        self.testbed.init_urlfetch_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_logservice_stub()

        # Remove agressive logging
        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.INFO)
        for handler in rootLogger.handlers:
            if isinstance(handler, logging.StreamHandler):
                rootLogger.removeHandler(handler)

    def beforeTest(self, test):
        try:
            self.testbed.deactivate()
        except:
            pass
