from django.contrib import admin
from .models import Plan, PlanItem, Promotion, Coupon


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