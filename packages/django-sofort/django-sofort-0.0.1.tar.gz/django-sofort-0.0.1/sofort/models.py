from django.db import models
from django.utils import translation
from moneyed import Money


class BaseResponseModel(models.Model):
    raw = models.TextField(max_length=9999)


class StatusHistoryItem(BaseResponseModel):
    time = models.DateTimeField()
    status = models.CharField(max_length=20)
    status_reason = models.CharField(max_length=255)


class Warning(BaseResponseModel):
    code = models.IntegerField()
    message = models.TextField(max_length=255)


class TransactionDetails(BaseResponseModel):
    project = models.IntegerField()
    test = models.BooleanField()
    time = models.DateTimeField()
    status = models.CharField(max_length=20)
    status_reason = models.TextField(max_length=255)
    status_modified = models.DateTimeField()
    status_history_items = models.ManyToManyField(StatusHistoryItem)
    payment_method = models.CharField(max_length=7)
    language_code = models.CharField(max_length=2, default=translation.get_language())
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    amount_refunded = models.DecimalField(max_digits=8, decimal_places=2)
    currency_code = models.CharField(max_length=3)

    @property
    def money(self):
        return Money(self.amount, self.currency_code)


class Transaction(BaseResponseModel):
    transaction_ref = models.CharField(max_length=27)
    payment_url = models.URLField()
    transaction_details = models.OneToOneField(TransactionDetails, blank=True, null=True)
    warnings = models.ManyToManyField(Warning)