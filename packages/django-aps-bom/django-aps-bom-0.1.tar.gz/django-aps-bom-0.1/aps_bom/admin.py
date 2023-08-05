"""Admin classes for the aps_bom app."""
from django.contrib import admin

from . import models


class AdditionalTextAdmin(admin.ModelAdmin):
    list_display = ['ipn', 'text']
    search_fields = ['ipn__code', 'text']


class BOMItemInline(admin.TabularInline):
    model = models.BOMItem


class BOMAdmin(admin.ModelAdmin):
    list_display = ['ipn', 'description']
    search_fields = ['ipn__code', 'description']
    inlines = [BOMItemInline, ]


class BOMItemAdmin(admin.ModelAdmin):
    list_display = ['ipn', 'bom', 'qty', 'unit', 'position']
    search_fields = ['ipn__code', 'bom__description']


class CBOMItemInline(admin.TabularInline):
    model = models.CBOMItem


class CBOMAdmin(admin.ModelAdmin):
    list_display = ['customer', 'description', 'html_link', 'product',
                    'version_date']
    search_fields = ['customer__description', 'description', 'product']
    inlines = [CBOMItemInline, ]


class CBOMItemAdmin(admin.ModelAdmin):
    list_display = ['bom', 'epn', 'qty', 'unit', 'position']
    search_fields = ['bom__description', 'bom__product', 'epn']


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'country']
    search_fields = ['country', 'code', 'description']
    list_fiter = ['country', ]


class CountryAdmin(admin.ModelAdmin):
    list_display = ['code', 'description']
    search_fields = ['description']


class EPNAdmin(admin.ModelAdmin):
    list_display = ['company', 'cpn', 'epn', 'ipn', 'description']
    search_fields = ['company__description', 'cpn__code', 'epn', 'ipn__code'
                     'description']


class IPNAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'price_group', 'shape', 'price_max']
    search_fields = ['code', 'name']
    list_filter = ['price_group']


class PriceGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'add', 'rate']


class PriceMarkerAdmin(admin.ModelAdmin):
    list_display = ['ipn', 'price', 'date']
    search_fields = ['ipn__code']


class ShapeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


class UnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'description']
    search_fields = ['code', 'description']


admin.site.register(models.AdditionalText, AdditionalTextAdmin)
admin.site.register(models.BOM, BOMAdmin)
admin.site.register(models.BOMItem, BOMItemAdmin)
admin.site.register(models.CBOM, CBOMAdmin)
admin.site.register(models.CBOMItem, CBOMItemAdmin)
admin.site.register(models.Company, CompanyAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.EPN, EPNAdmin)
admin.site.register(models.IPN, IPNAdmin)
admin.site.register(models.PriceGroup, PriceGroupAdmin)
admin.site.register(models.PriceMarker, PriceMarkerAdmin)
admin.site.register(models.Shape, ShapeAdmin)
admin.site.register(models.Unit, UnitAdmin)
