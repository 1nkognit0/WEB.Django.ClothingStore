from django.urls import path

from products.views import ProductListView, basket_add, basket_remove

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('category/<int:category_id>', ProductListView.as_view(), name='category'),
    path('page/<int:page>', ProductListView.as_view(), name='pages'),
    path('basket/add/<int:product_id>', basket_add, name='basket_add'),
    path('basket/remove/<int:basket_id>', basket_remove, name='basket_remove'),
]
