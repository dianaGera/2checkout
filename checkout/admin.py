from django.contrib import admin
from .models import Plan, PlanItem, Subscription, Promotion

admin.site.register(Plan)
admin.site.register(PlanItem)
admin.site.register(Promotion)



@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'subscription_code', 'start_date', 'expiration_date', 'auto_update', )
    fields = ('user', 'plan', 'subscription_code', 'start_date', 'expiration_date', 'extend', 'auto_update', 'trial', 'promotion')

    readonly_fields = ("start_date", "expiration_date")


# @admin.register(Promotion_fixed)
# class Promotion_percentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'coupon', 'currency', 'cycles')


# @admin.register(Promotion_percent)
# class Promotion_percentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'percent', 'cycles')