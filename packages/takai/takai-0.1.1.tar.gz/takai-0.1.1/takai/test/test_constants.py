# testing all constants used

import unittest
from takai.constants import *

class ConstantsTest(unittest.TestCase):
    '''Tests all constants defined in takai/takai/constants.py'''

    def test_http_request_parameters(self):
      self.assertEqual(PROTOCOL, 'https')
      self.assertEqual(DOMAIN, 'mpowerpayments.com')
      self.assertEqual(VERSION, 'v1')
      self.assertEqual(USER_AGENT, 'Pretty Egbert')
      self.assertEqual(REST_SUBDOMAIN, 'app')
      self.assertEqual(REST_SOCKET_TIMEOUT, 5)


    def test_http_rest_endpoints(self):
      endpoints = {
          'checkout-invoice/create',
          'opr/create',
          'opr/charge',
          'direct-pay/credit-account',
          'direct-card/processcard',
          'checkout-invoice/confirm/'
      }

      self.assertEqual(endpoints, set(REST_ENDPOINTS.keys()))

    def test_http_rest_endpoints_methods(self):
      for endpoint in REST_ENDPOINTS.keys():
        if endpoint.endswith('confirm/'):
          self.assertEqual(REST_ENDPOINTS[endpoint], HttpMethods.GET)

        else:
          self.assertEqual(REST_ENDPOINTS[endpoint], HttpMethods.POST)
