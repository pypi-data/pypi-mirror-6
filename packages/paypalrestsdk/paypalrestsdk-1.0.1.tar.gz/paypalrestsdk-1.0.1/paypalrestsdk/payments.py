from paypalrestsdk.resource import List, Find, Create, Post


class Payment(List, Find, Create, Post):
    """Payment class wrapping the REST v1/payments/payment endpoint

    Usage::

        >>> payment_histroy = Payment.all({"count": 5})
        >>> payment = Payment.find("PAY-1234")
        >>> payment = Payment.new({"intent": "sale"})
        >>> payment.create()     # return True or False
        >>> payment.execute({"payer_id": 1234})  # return True or False
    """
    path = "v1/payments/payment"

    def execute(self, attributes):
        return self.post('execute', attributes, self)

Payment.convert_resources['payments'] = Payment
Payment.convert_resources['payment'] = Payment


class Sale(Find, Post):
    """Sale class wrapping the REST v1/payments/sale endpoint

    Usage::

        >>> sale = Sale.find("98765432")
        >>> refund = sale.refund({"amount": {"total": "1.00", "currency": "USD"}})
        >>> refund.success()   # return True or False
    """
    path = "v1/payments/sale"

    def refund(self, attributes):
        return self.post('refund', attributes, Refund)

Sale.convert_resources['sales'] = Sale
Sale.convert_resources['sale'] = Sale


class Refund(Find):
    """Get details for a refund on direct or captured payment

    Usage::

        >>> refund = Refund.find("12345678")
    """
    path = "v1/payments/refund"

Refund.convert_resources['refund'] = Refund


class Authorization(Find, Post):
    """Enables looking up, voiding and capturing authorization and reauthorize payments

    Helpful links::
    https://developer.paypal.com/docs/api/#authorizations
    https://developer.paypal.com/docs/integration/direct/capture-payment/#authorize-the-payment

    Usage::

        >>> authorization = Authorization.find("")
        >>> capture = authorization.capture({ "amount": { "currency": "USD", "total": "1.00" } })
        >>> authorization.void() # return True or False
    """
    path = "v1/payments/authorization"

    def capture(self, attributes):
        return self.post('capture', attributes, Capture)

    def void(self):
        return self.post('void', {}, self)

    def reauthorize(self):
        return self.post('reauthorize', self, self)

Authorization.convert_resources['authorization'] = Authorization


class Capture(Find, Post):
    """Look up and refund captured payments, wraps v1/payments/capture

    Usage::

        >>> capture = Capture.find("")
        >>> refund = capture.refund({ "amount": { "currency": "USD", "total": "1.00" }})
    """
    path = "v1/payments/capture"

    def refund(self, attributes):
        return self.post('refund', attributes, Refund)

Capture.convert_resources['capture'] = Capture
