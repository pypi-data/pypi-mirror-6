#This is how you make money: others pay you!

__author__ = 'Yaw Boakye Yiadom'
__date__   = 'October 10, 2013'
__license__ = 'MIT'


'''
There are two (2) ways of letting your users pay their money.
1) Redirect: They are redirected to MPower's website and they perform
the payment
2) OnSite:   All the payment processes occur on your website.

The _Redirect_ option is available to every store owner, even
non-MPower account holders can use it to bill customers who already
have MPower accounts

The _OnSite_ option is reserved for store owners who are themselves
MPower accounts holders. For purposes of SEO and shit like that,
signup for an MPower account and use this option.
'''


#All (custom) Exceptions throwable during checkout
class CheckoutException(Exception):
    '''For when a checkout goes terribly wrong'''
    def __init__(self, msg):
        super().__init__(msg)


class InvoiceException(Exception):
    '''For when an improper invoice is created'''
    def __init__(self, msg):
        super().__init__(msg)


class InvoiceItemException(TypeError):
    '''?'''
    def __init__(self, msg):
        super().__init__(msg)


from collections import defaultdict, namedtuple


class InvoiceItem:
    def __init__(self, name, quantity, unit_price, total_price=None, desc=None):
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price or quantity*float(unit_price)
        self.description = desc

    def __eq__(self, other):
        if type(other) is not type(self):
            raise InvoiceException('Item should be instance of %s' % type(self))
        return self.name.lower() == other.name.lower()

    def __repr__(self):
        return '<#InvoiceItem (%s: %s, qty=%.2f, total=%.4f)' % (
                          self.name,
                          self.description,
                          self.quantity,
                          self.total_price
                        )


class InvoiceException(Exception):
    '''For when an improper invoice is created'''
    def __init__(self, msg):
        Exception.__init__(InvoiceException, msg)


class Invoice:
    def __init__(self, customer=None):
        self.items = []
        #TODO: Confirmation of customer credential? I have to check API
        self.customer = customer

    def _add(self, item): self.items.append(item)
    def total(self): return sum(item.total_price for item in self.items)

    def add_item(self, *a, **kw):
        '''Add an invoice item.'''
        if type(a[0]) is InvoiceItem:
            self._add(a[0])
            return

        self.items.append(InvoiceItem(*a, **kw))


    # FIXME: Is a remove item necessary? I don't really know.
    # This method is not specificied by the MPower Payments API documentation.
    def remove_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return a.remove(item)


    def __repr__(self):
        return '\n'.join(str(item) for item in self.items) + \
               '\nQuantity: %.2f, Total: %.4f' % (len(self.items), self.total())


    def __add__(self, *a, **kw): self.add_item(*a, **kw)
    def __sub__(self, name): self.remove_item(name)


class Checkout:
    def __init__(self, invoice):
        self._invoice = invoice

    @property
    def invoice(self):
        return self._invoice


class RedirectCheckout(Checkout):
    '''
    If you don't have an MPower account, this is the only option
    available to you to you to accept payments from MPower users.

    When your client decides to pay via their MPower accounts, they get
    redirected to main MPower Payments application
    (https://app.mpowerpayments.com) to transact the payment. They are
    automatically redirected back to your service when they're done.

    Q: What happens if they cancel the transaction on MPower's side?
    A: I have no idea. Ask Alfred Rowe (@nukturnal on Twitter) or anyone
    on his team

    How it works
    ============
    '''
    def __init__(self, invoice):
        super().__init__(invoice)



class OnSiteCheckout(Checkout):
    '''
    IMO this is the best option for you. For at least SEO reasons and to
    increase your chances of the client going through with the deal.

    Everything happens on your platform: paying and confirming receipt
    of value of payment. The conditional is, you should have an MPower
    account. If you don't have one already you can sign up for one at
    http://mpowerpayments.com

    How it works
    ============
    '''
    def __init__(self, invoice):
        super().__init__(invoice)
