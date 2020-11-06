from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('app.urls')),
    path('account/', include(('accounts.urls', 'accounts'))),
    path('admin/', admin.site.urls),
    path('subscription/', include('checkout.urls'))
]
