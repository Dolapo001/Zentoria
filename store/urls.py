from django.urls import path

from .views import (
    CartListView,
    CartItemListView,
    CartView,
    CartItemView,
    OrderListView,
    OrderItemList,
    OrderView,
    OrderItemView,
    PaymentView,
    AddressView,
    AddressDetailView,
    PaymentDetailView
)

urlpatterns = [
    path('carts/', CartListView.as_view(), name='cart-list'),
    path('cart-items/', CartItemListView.as_view(), name='cart-item-list'),
    path('carts/<int:cart_id>/', CartView.as_view(), name='cart-detail'),
    path('cart-items/<int:cart_item_id>/', CartItemView.as_view(), name='cart-item-detail'),

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:order_id>/', OrderView.as_view(), name='order-detail'),
    path('order-items/', OrderItemList.as_view(), name='order-item-list'),
    path('order-items/<int:order_item_id>/', OrderItemView.as_view(), name='order-item-detail'),

    path('payments/', PaymentView.as_view(), name='payment-list'),
    path('payments/<int:payment_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('addresses/', AddressView.as_view(), name='address-list'),
    path('addresses/<int:address_id>/', AddressDetailView.as_view(), name='address-detail'),
]
