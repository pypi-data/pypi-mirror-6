'''
    As at October 7, 2013 all MPower Payments endpoints are captured below.

    MPower Payments API v1

    PROTOCOL://{subdomain}.DOMAIN/{api_type}/VERSION/{resource}/{action}

    Depending on whether you're hitting live or sandbox endpoint, {api_type} could be `api` or `sandbox-api`
'''

__author__  = 'Yaw Boakye Yiadom'
__date__    = 'October 7, 2013'
__license__ = 'MIT'


from collections import namedtuple

#MPower uses HTTPS for all their endpoints
PROTOCOL            = 'https'
DOMAIN              = 'mpowerpayments.com'
VERSION             = 'v1'
USER_AGENT          = 'Pretty Egbert'
REST_SUBDOMAIN      = 'app'
REST_SOCKET_TIMEOUT = 5

Methods = namedtuple('Methods', ['POST', 'GET'])
HttpMethods = Methods('POST', 'GET')

REST_ENDPOINTS = {
    'checkout-invoice/create'   : HttpMethods.POST, #REDIRECT_CHECKOUT_INVOICE
    'opr/create'                : HttpMethods.POST, #ONSITE_PAYMENT_REQUEST_TOKEN
    'opr/charge'                : HttpMethods.POST, #ONSITE_PAYMENT_REQUEST_CHARGE
    'direct-pay/credit-account' : HttpMethods.POST, #DIRECT_PAY
    'direct-card/processcard'   : HttpMethods.POST, #DIRECT_CARD
    'checkout-invoice/confirm/' : HttpMethods.GET   #INVOICE_STATUS
}

