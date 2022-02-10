from django.contrib import admin
from .models import Plan, PlanItem, Subscription, Promotion, Coupon


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'plan', 'subscription_code', 'start_date', 'expiration_date', 'auto_update', 'promotion')
    fields = ('user', 'plan', 'subscription_code', 'start_date', 'expiration_date', 'extend', 'auto_update', 'trial', 'promotion')

    # readonly_fields = ("start_date", "expiration_date")


class PlanAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'period', 'price', 'product_id', 'code']
    list_editable = ['price', 'product_id', 'code']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['pk', 'coupon', 'active']


admin.site.register(Plan, PlanAdmin)
admin.site.register(PlanItem)
admin.site.register(Promotion)
admin.site.register(Coupon, CouponAdmin)

# @admin.register(Promotion_fixed)
# class Promotion_percentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'coupon', 'currency', 'cycles')


# @admin.register(Promotion_percent)
# class Promotion_percentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'percent', 'cycles')