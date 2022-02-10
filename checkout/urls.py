from django.urls import path
from .views import subscription_api, change_subscription, subscription_service, checkout, stop_auto_subscription, \
    enable_auto_subscription, create_order, apply_vouchers, promotion_cod

urlpatterns = [
    path('api/', subscription_api, name='subscription_api'),
    path("api/order/", create_order, name="create_order"),
    path("api/get_coupon_code/", promotion_cod, name="promotion_cod"),
    path('service/', subscription_service, name='subscription_service'),
    path('api/<int:pk>/', checkout, name='check'),
    path('stop_subscription/<int:pk>/', stop_auto_subscription, name='stop_auto_subscription'),
    path('enable_subscription/<int:pk>/', enable_auto_subscription, name='enable_auto_subscription'),
    path('change_subscription/', change_subscription, name='change_subscription'),
    path('apply_coupon/<int:pk>/<int:coupon_id>/', apply_vouchers, name='apply_vouchers')
]
