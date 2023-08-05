#!/usr/bin/env python
import string
import random
import urllib
import urllib2
from datetime import datetime, date, tzinfo, timedelta
from google.appengine.ext import ndb
from google.appengine.ext import deferred


class BasePesapalPayment(ndb.Model):

    STATUSES = {
        0: 'pending',
        1: 'completed',
        2: 'failed',
        3: 'invalid',
        4: 'refunded',
        5: 'overdue'
    }

    MAX_STATUS_CHECKS = 5

    DEFER_STATUS_CHECK_BY_MINUTES = 60

    date_created = ndb.DateTimeProperty(
        auto_now_add=True
    )
    date_updated = ndb.DateTimeProperty(
        auto_now=True
    )
    status = ndb.IntegerProperty(
        choices=STATUSES.keys(),
        default=0
    )
    amount = ndb.IntegerProperty(
        required=True
    )
    transaction_tracking_id = ndb.StringProperty(
        required=True
    )
    merchant_reference = ndb.StringProperty(
        required=True
    )
    ref = ndb.StringProperty(
        required=True
    )
    method = ndb.StringProperty(
        #required=True
    )

    @classmethod
    def get_ref(cls):
        ref = None
        while True:
            chars = string.digits + string.ascii_letters
            ref = ''.join(
                random.choice(chars) for i in range(20)
            )
            if not cls.gql(
                'WHERE ref=:1', ref
            ).get():
                break
        return ref

    def get_status_int(self, status):
        return dict(
            [(y, x) for x, y in self.STATUSES.iteritems()]
        )[status]

    def get_status_string(self):
        return self.STATUSES[self.status]

    def get_is_overdue(self):

        status_string = self.get_status_string()

        if status_string == 'completed':
            return False

        elif status_string != 'pending':
            return True

        timeout = self.MAX_STATUS_CHECKS*self.DEFER_STATUS_CHECK_BY_MINUTES
        return timedelta(minutes=timeout) <= (datetime.now() - self.date_created)

    def get_is_pending(self):
        return self.get_status_string() in ['pending', 'overdue']

    def get_is_done(self):
        return not self.is_pending

    def set_status(self, status_string):
        status = self.get_status_int(status_string)
        self.status = status

    def check_status(self, client):

        data = {
          'pesapal_merchant_reference': self.ref,
          'pesapal_transaction_tracking_id': self.transaction_tracking_id
        }
        request = client.queryPaymentDetails(data)
        url = request.to_url()

        ctx = ndb.get_context()
        res = ctx.urlfetch(url).get_result()

        data = res.content

        if 'pesapal_response_data=' not in data:
            return

        pesapal_transaction_tracking_id,\
        payment_method,\
        payment_status,\
        pesapal_merchant_reference = data\
            .split('pesapal_response_data=')[1]\
            .split(',')

        self.method = payment_method
        self.set_status(payment_status.lower())
        self.put()

        if self.get_status_string() != 'pending':
            return

        # mark overdue if payment status check timed out
        timeout = self.MAX_STATUS_CHECKS*self.DEFER_STATUS_CHECK_BY_MINUTES

        payment_overdue = timedelta(minutes=timeout) <= (datetime.now() - self.date_created)

        if payment_overdue:
            self.set_status('overdue')
            self.put()
        else:
            deferred.defer(
                self.check_status,
                client,
                _countdown=self.DEFER_STATUS_CHECK_BY_MINUTES
            )
