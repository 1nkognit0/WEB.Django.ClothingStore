from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.core import serializers
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from ipaddress import ip_address, ip_network

from yookassa import Configuration, Payment
import json

from orders.forms import OrderForm
from common.views import TitleMixin
from products.models import Basket
from orders.models import Orders

# конфигурация юкассы
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

# Список IP-адресов ЮКассы для проверки безопасности
YOOKASSA_TRUSTED_NETWORKS = [
    '185.71.76.0/27',
    '185.71.77.0/27',
    '77.75.153.0/25',
    '77.75.154.128/25',
    '2a02:5180::/32',
    '77.75.156.11/32',
    '77.75.156.35/32'
]


class OrderCreateView(TitleMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    title = 'Оформление заказа'
    success_url = reverse_lazy('orders:order_success')

    def form_valid(self, form):
        current_user = self.request.user
        queryset = Basket.objects.filter(user=current_user)
        form.instance.busket_history = serializers.serialize('json', queryset)
        form.instance.initiator = current_user

        # Сохраняем заказ
        self.object = form.save()

        # Создаем платеж в ЮКассе
        payment_url = self.create_yookassa_payment()

        if payment_url:
            # Перенаправляем на страницу оплаты ЮКассы
            return redirect(payment_url)
        else:
            form.add_error(None, 'Ошибка создания платежа')
            return self.form_invalid(form)

    def create_yookassa_payment(self):
        try:
            baskets = Basket.objects.filter(user=self.request.user)
            total_amount = baskets.total_sum()

            payment = Payment.create({
                "amount": {
                    "value": f"{total_amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.request.build_absolute_uri(
                        reverse('orders:order_success')
                    )
                },
                "capture": True,
                "description": f"Заказ №{self.object.id}",
                "metadata": {
                    "order_id": self.object.id
                }
            })

            return payment.confirmation.confirmation_url

        except Exception as e:
            print(f"Error creating payment: {e}")
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['baskets'] = Basket.objects.filter(user=self.request.user)
        return context


@csrf_exempt
def yookassa_webhook_view(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    # Получаем реальный IP-адрес клиента
    client_ip = get_client_ip(request)
    print(f"Webhook request from IP: {client_ip}")  # Для дебага

    # Проверяем IP
    if not is_yookassa_ip(client_ip):
        print(f"⚠️ SUSPICIOUS WEBHOOK from untrusted IP: {client_ip}")
        return HttpResponse('Forbidden: Invalid IP address', status=403)

    print(f"✅ Webhook from trusted YooKassa IP: {client_ip}")

    try:
        event_json = json.loads(request.body)
        event_type = event_json.get('event')
        payment_object = event_json.get('object', {})

        # Обрабатываем только событие успешной оплаты
        if event_type == 'payment.succeeded':
            payment_id = payment_object.get('id')

            # Получаем платеж из ЮКассы для проверки
            payment = Payment.find_one(payment_id)

            if payment.status == 'succeeded':
                order_id = payment.metadata.get('order_id')

                if order_id:
                    order = Orders.objects.get(id=order_id)
                    # Меняем статус заказа с 0 (Создан) на 1 (Оплачен)
                    order.status = Orders.PAID
                    order.save()

                    # Очищаем корзину
                    Basket.objects.filter(user=order.initiator).delete()
                    print(f"✅ Order {order_id} marked as paid")

                    return HttpResponse('Webhook processed successfully', status=200)

        return HttpResponse('Webhook received but not processed', status=200)

    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)
    except Orders.DoesNotExist:
        return HttpResponse('Order not found', status=404)
    except Exception as e:
        print(f"Webhook error: {e}")
        return HttpResponse('Server error', status=500)


class OrderSuccessView(TitleMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Заказ успешно создан'


class OrdersView(TitleMixin, TemplateView):
    template_name = 'orders/orders.html'
    title = 'Заказы'


def is_yookassa_ip(ip_str):
    """Проверяет, принадлежит ли IP доверенным сетям ЮКассы"""
    try:
        client_ip = ip_address(ip_str)
        for network in YOOKASSA_TRUSTED_NETWORKS:
            if client_ip in ip_network(network):
                return True
        return False
    except ValueError:
        return False

def get_client_ip(request):
    """Получаем реальный IP-адрес клиента с учетом прокси"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Берем первый IP из списка (реальный клиент)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip