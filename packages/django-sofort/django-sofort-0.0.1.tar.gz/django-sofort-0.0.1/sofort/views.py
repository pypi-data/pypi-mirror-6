from django.http import HttpResponse
from sofort import BaseResponse
from sofort.models import Transaction


def notification(request):
    if request.method == 'POST':
        response = BaseResponse.factory(request.body)
        try:
            t = Transaction.objects.get(transaction_ref=response.transaction)
            t.raw = response.raw
        except Exception, e:
            print(e)

    return HttpResponse()