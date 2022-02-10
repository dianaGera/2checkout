from django.urls import path
from .views import home, admin_action

urlpatterns = [
    path('', home, name='home'),
    path('admin/dashboard/', admin_action, name='admin_action')
]
