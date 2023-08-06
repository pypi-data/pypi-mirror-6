from abc import ABCMeta, abstractproperty
from dict2xml import dict2xml
from django.core.urlresolvers import reverse
from django.utils import translation
import requests
from moneyed import Money
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from appconf import AppConf

import models


class SofortConf(AppConf):
    API_URL = 'https://api.sofort.com/api/xml'
    SUCCESS_URL = 'https://example.com/success'

    class Meta:
        prefix = 'SOFORT'
        required = ['ID', 'KEY', 'PROJECT']


settings = SofortConf()


def soup_property(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs).get_text()
    return inner


def create_transaction(money, project_id, reasons=(), user_variables=()):
    m = Multipay(money, project_id, reasons, user_variables)
    response = m.execute()
    transaction = models.Transaction(transaction=response.transaction, payment_url=response.payment_url)
    transaction.save()
    for warning in response.warnings:
        w = models.Warning(code=warning.code, message=warning.code)
        w.save()
        transaction.warnings.add(w)
    transaction.save()
    return transaction


class BaseResponse(object):
    __metaclass__ = ABCMeta

    def __init__(self, response):
        self._raw = response
        self.bs = BeautifulSoup(response)

    @property
    def raw(self):
        return self._raw

    @staticmethod
    def factory(response):
        bs = BeautifulSoup(response)
        if bs.new_transaction:
            return NewTransaction(response)
        elif bs.status_notification:
            return StatusNotification(response)
        elif bs.transactions:
            return Transactions(response)
        elif bs.errors:
            return Errors(response)


class Warning(BaseResponse):

    @property
    @soup_property
    def code(self):
        return self.bs.code

    @property
    @soup_property
    def message(self):
        return self.bs.message


class NewTransaction(BaseResponse):
    @property
    @soup_property
    def transaction(self):
        return self.bs.transaction

    @property
    @soup_property
    def payment_url(self):
        return self.bs.payment_url

    @property
    def warnings(self):
        lst = []
        if self.bs.warnings:
            for warning in self.bs.warnings:
                lst.append(Warning(warning))
        return lst


class StatusNotification(BaseResponse):
    @property
    @soup_property
    def transaction(self):
        return self.bs.transaction

    @property
    def time(self):
        dt = date_parser.parse(self.bs.time.get_text())
        return dt


class Transactions(BaseResponse):
    pass


class Errors(BaseResponse):
    pass


class BaseRequest(object):
    __metaclass__ = ABCMeta

    _raw = ''
    _raw_response = ''
    _response = None

    @abstractproperty
    def response_class(self):
        pass

    @abstractproperty
    def root_element(self):
        pass

    @property
    def raw(self):
        self.create_query_xml()
        return self._raw

    @property
    def raw_response(self):
        return self._raw_response

    @property
    def response(self):
        if not self._response:
            self._response = BaseResponse.factory(self.raw_response)
        return self._response

    def execute(self):
        self._raw_response = requests.post(settings.API_URL, data=dict2xml(self.raw), auth=(settings.ID, settings.KEY))
        self._response = BaseResponse.factory(self.raw_response)
        return self.response

    @abstractproperty
    def query_dict(self):
        pass

    def create_query_xml(self):
        self._raw = dict2xml(self.query_dict, wrap=self.root_element)


class Multipay(BaseRequest):
    response_class = NewTransaction
    root_element = 'multipay'

    def __init__(self, money, project_id, reasons=(), user_variables=()):
        if not isinstance(money, Money):
            raise ValueError('%(money) should be of Money', params={'money': money.__class__.__name__})

        self.money = money
        self.project_id = project_id
        self.reasons = reasons
        self.user_variables = user_variables

    @property
    def query_dict(self):
        multipay = {
            'langauge_code': translation.get_language(),
            'amount': self.money.amount,
            'currency_code': self.money.currency,
            'reasons': {'reason': self.reasons + ('-TRANSACTION-', )},
            'user_variables': {'user_variable': self.user_variables},
            'success_url': settings.SUCCESS_URL,
            'success_link_redirect': '',
            'abort_url': '',
            'notification_urls': {'notification_url': (reverse('sofort-notification'))},
            'su': ''
        }
        return multipay