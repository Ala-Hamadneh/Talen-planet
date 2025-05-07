from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderStatus

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'active_order_count')
    search_fields = ('name', 'description')
    readonly_fields = ('name',)  
    
    def active_order_count(self, obj):
        return obj.orders.filter(is_active=True).count()
    active_order_count.short_description = 'Active Orders'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'gig_title',
        'short_requirements',
        'buyer_username',
        'seller_username',
        'status',
        'formatted_price',
        'created_short',
        'active_status',  
        'is_active'  
    )
    list_editable = ('is_active',)  
    list_filter = ('is_active', 'status')  
    
    def buyer_username(self, obj):
        return obj.buyer.username
    buyer_username.short_description = 'Buyer'
    
    def seller_username(self, obj):
        return obj.gig.seller.username
    seller_username.short_description = 'Seller'
    
    def gig_title(self, obj):
        return obj.gig.title
    gig_title.short_description = 'Gig'
    
    def formatted_price(self, obj):
        return f"{obj.gig.price:,.2f} ILS"
    formatted_price.short_description = 'Price'
    
    def short_requirements(self, obj):
        return f"{obj.requirements[:50]}..." if len(obj.requirements) > 50 else obj.requirements
    short_requirements.short_description = 'Requirements'
    
    def created_short(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_short.short_description = 'Created'
    
    def active_status(self, obj):
        color = 'green' if obj.is_active else 'red'
        icon = '✔' if obj.is_active else '✘'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, icon
        )
    active_status.short_description = 'Active Status'
    
    def get_queryset(self, request):
        """Optimize query by selecting related fields"""
        return super().get_queryset(request).select_related(
            'buyer',
            'gig',
            'gig__seller',
            'status'
        )