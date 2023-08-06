from django.core.urlresolvers import reverse
from django.test import TestCase
from moneyed import Money
from sofort import Multipay, NewTransaction
from sofort.models import Transaction


RAW_MULTIPAY = """<multipay>
  <abort_url></abort_url>
  <amount>2.2</amount>
  <currency_code>EUR</currency_code>
  <langauge_code>en-us</langauge_code>
  <notification_urls>
    <notification_url>/</notification_url>
  </notification_urls>
  <reasons>
    <reason>Testueberweisung</reason>
    <reason>-TRANSACTION-</reason>
  </reasons>
  <su></su>
  <success_link_redirect></success_link_redirect>
  <success_url>https://example.com/success</success_url>
  <user_variables>
    <user_variable>test</user_variable>
  </user_variables>
</multipay>"""

RAW_NEW_TRANSACTION = """<?xml version="1.0" encoding="UTF-8" ?>
<new_transaction>
      <transaction>99999-53245-5483-4891</transaction>
      <payment_url>https://www.sofort.com/payment/go/508712aa8572615d6151de6111349bc5872435987c23c</payment_url>
</new_transaction>"""


class TestObjects(TestCase):
    urls = 'sofort.urls'

    def test_multipay(self):
        mp = Multipay(Money(2.2, 'EUR'), 53245, ('Testueberweisung',), ('test', ))
        self.assertEqual(mp.raw, RAW_MULTIPAY)

        mp._raw_response = RAW_NEW_TRANSACTION

        self.assertIsInstance(mp.response, NewTransaction)
        self.assertEqual(mp.response.raw, RAW_NEW_TRANSACTION)

    def test_create_transaction(self):
        t = Transaction(transaction_ref='99999-53245-5483-4891',
                        payment_url='https://www.sofort.com/payment/go/508712aa8572615d6151de6111349bc5872435987c23c',
                        raw=RAW_NEW_TRANSACTION)
        t.save()
        self.assertEqual(Transaction.objects.count(), 1)

    def test_response(self):
        self.test_create_transaction()
        self.client.post(reverse('sofort-notification'), content_type='application/xml', data=RAW_NEW_TRANSACTION)
