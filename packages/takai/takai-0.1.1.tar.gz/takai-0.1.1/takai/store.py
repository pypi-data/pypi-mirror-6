'''Your store's information goes here. Make sure to get it right'''

__author__  = 'Yaw Boakye Yiadom'
__date__    = 'October 9, 2013'
__license__ = 'MIT'


class Store(object):
    '''
    A Store is a registered <tt>MPower</tt> account, with extra information about the shop for preparing invoices,receipts, etc.

    Phone number used in creating store should be the same as MPower account (phone) number for the shop
    '''
    def __init__(self, name, tagline, postal_addr, phone_no, **kwargs):
        self.name = name
        self.tagline = tagline
        self.postal_address = postal_addr
        self.phone_number = phone_no
        for key, value in kwargs.items():
            setattr(self, key, value)



class StoreException(Exception):
    pass
