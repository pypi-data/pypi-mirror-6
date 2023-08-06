import unittest
from takai.store import Store


class StoreTests(unittest.TestCase):
    '''Tests for registering an MPower Store'''

    def setUp(self):
        self.lindas = Store(
          'http://88 Places',
          'Food anytime!',
          '12 Coconut Avenue, SJ Estate, P O Box 22, Obuasi, Ashanti',
          '+2330233101101',
          website_url='http://88p.co',
          logo_url='http://88p.co/brand/logo-max.png',
          return_url='http://88p.co/paid',
          cancel_url='http://88p.co/cancelled'
        )

    def test_get_store_parameters(self):
        self.assertEqual('http://88 Places', self.lindas.name)
        self.assertEqual('Food anytime!', self.lindas.tagline)
        self.assertEqual('+2330233101101', self.lindas.phone_number)
        self.assertEqual('http://88p.co', self.lindas.website_url)
        self.assertEqual('http://88p.co/brand/logo-max.png', self.lindas.logo_url)
        self.assertEqual('http://88p.co/paid', self.lindas.return_url)
        self.assertEqual('http://88p.co/cancelled', self.lindas.cancel_url)
        self.assertEqual(
          '12 Coconut Avenue, SJ Estate, P O Box 22, Obuasi, Ashanti', self.lindas.postal_address
        )

    def test_store_set_postal_address(self):
        new_postal_address = '1 Apple Lane,PM Properties,P O Box 2,Obuasi,Ashanti'
        self.lindas.postal_address = new_postal_address
        self.assertEqual(new_postal_address, self.lindas.postal_address)

    def test_store_set_return_url(self):
        new_return_url = 'http://88p.co/new_return_url'
        self.lindas.return_url = new_return_url
        self.assertEqual('http://88p.co/new_return_url', self.lindas.return_url)

    def test_store_set_cancel_url(self):
        new_cancel_url = 'http://88p.co/new_cancel_url'
        self.lindas.cancel_url = new_cancel_url
        self.assertEqual('http://88p.co/new_cancel_url', self.lindas.cancel_url)


    def test_store_set_website(self):
        new_website_url = 'http://88places.co'
        self.lindas.website = new_website_url
        self.assertEqual('http://88places.co', self.lindas.website)
