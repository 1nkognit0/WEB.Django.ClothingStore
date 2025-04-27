from django.urls import path

from orders.views import OrderCreateView, OrdersView

app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrdersView.as_view(), name='orders'),
]
