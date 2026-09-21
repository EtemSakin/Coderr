from django.contrib import admin

from offers_app.models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'creator__username')


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'offer',
        'offer_type',
        'price',
        'delivery_time_in_days',
    )
    list_filter = ('offer_type',)
    search_fields = ('title', 'offer__title')
