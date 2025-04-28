from django.contrib import admin
from .models import Categories, Services, Gigs

@admin.register(Categories)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_count')
    search_fields = ('name',)
    prepopulated_fields = {'name': ('name',)}
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Number of Services'

@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_category', 'gig_count')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    list_select_related = ('category',)
    
    def get_category(self, obj):
        return obj.category.name
    get_category.short_description = 'Category'
    get_category.admin_order_field = 'category__name'
    
    def gig_count(self, obj):
        return obj.gigs.count()
    gig_count.short_description = 'Active Gigs'

@admin.register(Gigs)
class GigAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'get_seller', 
        'get_service', 
        'price', 
        'delivery_time', 
        'is_active', 
        'created_at'
    )
    list_filter = ('service', 'is_active', 'created_at')
    search_fields = (
        'title', 
        'seller__username', 
        'service__name',
        'description'
    )
    date_hierarchy = 'created_at'
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('seller', 'service', 'title', 'description')
        }),
        ('Pricing & Delivery', {
            'fields': ('price', 'delivery_time')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'seller', 
            'service', 
            'service__category'
        )
    
    def get_seller(self, obj):
        return obj.seller.username
    get_seller.short_description = 'Seller'
    get_seller.admin_order_field = 'seller__username'
    
    def get_service(self, obj):
        return f"{obj.service.name} ({obj.service.category.name})"
    get_service.short_description = 'Service'
    get_service.admin_order_field = 'service__name'