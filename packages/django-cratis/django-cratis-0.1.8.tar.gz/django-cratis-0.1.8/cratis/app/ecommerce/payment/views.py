from django.shortcuts import get_object_or_404
from django.views.generic.base import ContextMixin, View
from cratis.app.ecommerce.payment.models import PaymentMethod


class PaymentView(View):

    def load_method(self, method):
        return  get_object_or_404(PaymentMethod, slug=method)