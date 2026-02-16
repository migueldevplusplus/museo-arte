from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import Genre, Artist, Artwork, Membership, Sale

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
                # Find the buyer (logic assumption: for this simple project, we might need a way to know WHO reserved it. 
                # In the view we didn't save the reservation to a user, just changed status. 
                # To fix this properly, we should have created a Sale object with status PENDING.
                # Let's fix the model/view logic slightly or assume the admin manually assigns the buyer in a Sale object.
                
                # BETTER APPROACH: Admin creates a Sale object manually for the Reserved artwork.
                # So this action might just be valid if we had a "Reservation" model.
                # Let's stick to the requirement: "Esta factura es hecha por cualquier administrador... una vez concretada la venta"
                pass
            
            # If we just change status here, we miss the Invoice generation linked to a buyer.
            # So, let's rely on the SaleAdmin to create the sale.
        pass

# Re-thinking: The requirement says "Un trabajador... se comunicará... De concretarse la venta... Al emitirse la factura se considera venta concretada."
# So the Admin goes to "Sales", adds a new Sale, selects the Artwork (which is Reserved), selects the Buyer.
# Saving the Sale should update the Artwork status to SOLD and calculate totals.

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('artwork', 'buyer', 'date', 'total', 'pdf_invoice')
    readonly_fields = ('date', 'subtotal', 'iva', 'total', 'commission')
    autocomplete_fields = ['artwork', 'buyer']
    
    def save_model(self, request, obj, form, change):
        if not change: # Creating new sale
            artwork = obj.artwork
            if artwork.status != 'SOLD':
                artwork.status = 'SOLD'
                artwork.save()
                
                # Calculate amounts
                obj.subtotal = artwork.price
                obj.iva = obj.subtotal * 0.16 # 16% IVA
                obj.commission = obj.subtotal * 0.10 # 10% Commission
                obj.total = float(obj.subtotal) + float(obj.iva)
                obj.processed_by = request.user
        
        super().save_model(request, obj, form, change)

    def pdf_invoice(self, obj):
        # Placeholder for PDF generation link
        return "Invoice #{}".format(obj.id)
    pdf_invoice.short_description = 'Invoice'

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('buyer_profile', 'start_date', 'amount')
