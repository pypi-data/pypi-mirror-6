from google.appengine.ext import testbed
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub
from google.appengine.datastore import datastore_stub_util
from google.appengine.api.search.simple_search_stub import SearchServiceStub
from google.appengine.ext import deferred
import base64
import tempfile
import os
import logging


class SimpleTestBed(object):
    """
    Creates a limited testbed, this is used before loading test
    files to fix issues with modules that touch google services before
    an http request. This also fixes the httplib2 library from being
    obtuse during tests.
    """
    def __init__(self):
        self.testbed = testbed.Testbed()

    def activate(self):
        self.testbed.activate()
        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)
        self.testbed.init_urlfetch_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_logservice_stub()

    def deactivate(self):
        try:
            self.testbed.deactivate()
        except:
            pass


class FullTestBed(object):
    """
    Creates a full testbed for use during tests.
    """
    def __init__(self):
        self.testbed = testbed.Testbed()

    def activate(self):
        self.testbed.setup_env(
            AUTH_DOMAIN='gmail.com',
            APPLICATION_ID='_')

        self.testbed.activate()
        self.testbed.init_memcache_stub()

        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)
        self.testbed.init_taskqueue_stub(
            root_path=os.path.abspath(os.getcwd()))
        self.testbed.init_blobstore_stub()

        try:
            self.testbed.init_images_stub()
        except:
            logging.info("PIL couldn't be loaded so you can't test with the images service.")

        self.testbed.init_logservice_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_user_stub()
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        # Search, file, and blob stubs
        stub = SearchServiceStub()
        self.testbed._register_stub('search', stub)

        blob_storage = file_blob_storage.FileBlobStorage(
            tempfile.gettempdir(),
            testbed.DEFAULT_APP_ID)
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        self.testbed._register_stub('blobstore', blob_stub)
        self.testbed._register_stub('file', file_stub)

    def deactivate(self):
        try:
            self.testbed.deactivate()
        except:
            pass

    def run_deferred_tasks(self, queue='default'):
        tasks = self.taskqueue_stub.GetTasks(queue)
        while tasks:
            self.taskqueue_stub.FlushQueue(queue)
            for task in tasks:
                deferred.run(base64.b64decode(task['body']))
            tasks = self.taskqueue_stub.GetTasks(queue)

    def login_user(self, email, admin=False):
        self.testbed.setup_env(
            USER_EMAIL=email,
            USER_ID=email,
            USER_IS_ADMIN='1' if admin else '0',
            AUTH_DOMAIN='gmail.com',
            overwrite=True)
