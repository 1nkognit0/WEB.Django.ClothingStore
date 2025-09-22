from django.urls import path

from orders.views import OrderCreateView, OrdersView, OrderSuccessView, yookassa_webhook_view

app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('success/', OrderSuccessView.as_view(), name='order_success'),
    path('yookassa-webhook/', yookassa_webhook_view, name='yookassa_webhook'),
]
