import os

import sys
sys.path.insert(0, '/usr/local/google_appengine')
import dev_appserver
dev_appserver.fix_sys_path()

import mock
import logging
import webtest
import urllib2
import unittest

import webapp2 as webapp
from webapp2_extras.securecookie import SecureCookieSerializer
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import memcache
from google.appengine._internal.django.utils import simplejson as json

from views import app, sessions
from models import *


logger = logging.getLogger(__name__)


NOW = datetime(2012, 2, 1, 0, 0)


def mock_datetime(target):
    def wrapper(method):
        @mock.patch(target)
        def func(self, mock_datetime, mock_datetime2=None):
            mock_datetime.now.return_value = NOW
            mock_datetime.side_effect = datetime
            if mock_datetime2:
                mock_datetime2.now.return_value = NOW
                mock_datetime2.side_effect = datetime
                method(self, mock_datetime, mock_datetime2)
            else:
                method(self, mock_datetime)
        func.func_name = method.func_name
        return func
    return wrapper


def mock_urllib(status):
    def wrapper(method):
        @mock.patch('google.appengine.api.urlfetch.urlfetch_service_pb.URLFetchResponse')
        def func(self, URLFetchResponse):
            res = 'pesapal_response_data=efg,MPESA,%s,00' % status
            response = URLFetchResponse.return_value
            response.contentwastruncated.return_value = False
            response.statuscode.return_value = 200
            response.content.return_value = res
            method(self)
        func.func_name = method.func_name
        return func
    return wrapper


class TestCase(unittest.TestCase):

    @mock_datetime('models.datetime')
    @mock_datetime('google.appengine.ext.ndb.model.datetime.datetime')
    def setUp(self, mock_datetime, mock_datetime2):

        self.app = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub()
        
        self.testbed.get_stub('urlfetch')._Dynamic_Fetch = mock.Mock()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        self.testbed.setup_env(
            test = 'true',
            overwrite = True
        )

    def tearDown(self):
        self.testbed.deactivate()

    def get(self, path, data=None, session={}):

        secure_cookie_serializer = SecureCookieSerializer(
            SPLUNK_PROJECT_ID
        )
        serialized_session = secure_cookie_serializer.serialize(
            'session', session
        )
        headers = {'Cookie': 'session=%s' % serialized_session}
        if data:
            return self.app.post_json(
                path,
                data,
                headers=headers,
                expect_errors=True
            )
        return self.app.get(path, headers=headers)


class StatusCheckTestCase(TestCase):

    def setUp(self):

        super(StatusCheckTestCase, self).setUp()

        self.payment = Payment(
            status=1, # completed
            amount = 1000,
            transaction_tracking_id='',
            merchant_reference='',
            ref='boost'
        )
        self.payment.put()

    def tearDown(self):

        super(TestCase, self).tearDown()

        # assert method was saved
        assert self.payment.method == 'MPESA'

    @mock_urllib('PENDING')
    def test_pending(self):
        self.payment.check_status()
        assert self.payment.get_status_string() == 'pending'

    @mock_urllib('COMPLETED')
    def test_completed(self):
        self.payment.check_status()
        assert self.payment.get_status_string() == 'completed'

    @mock_urllib('FAILED')
    def test_failed(self):
        self.payment.check_status()
        assert self.payment.get_status_string() == 'failed'

    @mock_urllib('INVALID')
    def test_invalid(self):
        self.payment.check_status()
        assert self.payment.get_status_string() == 'invalid'

    @mock_urllib('REFUNDED')
    def test_refunded(self):
        self.payment.check_status()
        assert self.payment.get_status_string() == 'refunded'

    @mock_urllib('PENDING')
    def test_overdue(self):
        self.payment.date_created = datetime(1990, 7, 9)
        self.payment.put()
        self.payment.check_status()
        assert self.payment.get_status_string() == 'overdue'

unittest.main()
