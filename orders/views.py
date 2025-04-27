from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.core import serializers
from django.urls import reverse_lazy

from orders.forms import OrderForm
from common.views import TitleMixin
from products.models import Basket


class OrderCreateView(TitleMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    title = 'Оформление заказа'
    success_url = reverse_lazy('orders:orders')

    def form_valid(self, form):
        current_user = self.request.user
        queryset = Basket.objects.filter(user=current_user)
        form.instance.busket_history = serializers.serialize('json', queryset)
        form.instance.initiator = current_user
        return super().form_valid(form)


class OrdersView(TitleMixin, TemplateView):
    template_name = 'orders/orders.html'
    title = 'Заказы'

