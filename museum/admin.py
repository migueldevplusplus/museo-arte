from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import (
    Genre, Artist, Artwork, Membership, Sale,
    Painting, Sculpture, Photography, Ceramic, Goldsmithing,
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'birth_date')
    filter_horizontal = ('genres',)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'price', 'status', 'creation_date')
    list_filter = ('status', 'genre', 'artist')
    search_fields = ('title', 'artist__name')
    actions = ['mark_as_sold']

    @admin.action(description='Mark selected artworks as SOLD and generate Invoice')
    def mark_as_sold(self, request, queryset):
        for artwork in queryset:
            if artwork.status == 'RESERVED':
                pass
        pass


# ---- Specialized artwork admins ----

@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'technique', 'support', 'price', 'status')
    list_filter = ('technique', 'support', 'status')
    search_fields = ('title', 'artist__name')


@admin.register(Sculpture)
class SculptureAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'material', 'weight', 'price', 'status')
    list_filter = ('material', 'status')
    search_fields = ('title', 'artist__name')


@admin.register(Photography)
class PhotographyAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'photo_type', 'technique', 'price', 'status')
    list_filter = ('photo_type', 'technique', 'status')
    search_fields = ('title', 'artist__name')


@admin.register(Ceramic)
class CeramicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'material', 'technique', 'price', 'status')
    list_filter = ('material', 'status')
    search_fields = ('title', 'artist__name')


@admin.register(Goldsmithing)
class GoldsmithingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'material', 'object_type', 'price', 'status')
    list_filter = ('material', 'object_type', 'status')
    search_fields = ('title', 'artist__name')


# ---- Sale & Membership ----

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('artwork', 'buyer', 'date', 'total', 'pdf_invoice')
    readonly_fields = ('date', 'subtotal', 'iva', 'total', 'commission')
    autocomplete_fields = ['artwork', 'buyer']

    def save_model(self, request, obj, form, change):
        if not change:
            artwork = obj.artwork
            if artwork.status != 'SOLD':
                artwork.status = 'SOLD'
                artwork.save()

                obj.subtotal = artwork.price
                obj.iva = obj.subtotal * 0.16
                obj.commission = obj.subtotal * 0.10
                obj.total = float(obj.subtotal) + float(obj.iva)
                obj.processed_by = request.user

        super().save_model(request, obj, form, change)

    def pdf_invoice(self, obj):
        return "Invoice #{}".format(obj.id)
    pdf_invoice.short_description = 'Invoice'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('buyer_profile', 'start_date', 'amount')
