from django.contrib import admin
from .models import (
    UserProfile, State, District, Area, 
    Property, PropertyImage, UserSearchHistory
)

# =====================================================================
# User Profile Admin
# =====================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    
    list_display = ('user', 'role', 'phone', 'gender', 'created_at')
    list_filter = ('role', 'gender', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'bio')
        }),
        ('Personal Information', {
            'fields': ('phone', 'gender', 'birth_date', 'address', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# =====================================================================
# Location Admin (State, District, Area)
# =====================================================================

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    """Admin interface for State model."""
    
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    ordering = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """Admin interface for District model."""
    
    list_display = ('name', 'state', 'created_at')
    list_filter = ('state', 'created_at')
    search_fields = ('name', 'state__name')
    readonly_fields = ('created_at',)
    ordering = ('state', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('state', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin interface for Area model."""
    
    list_display = ('name', 'district', 'created_at')
    list_filter = ('district__state', 'district', 'created_at')
    search_fields = ('name', 'district__name')
    readonly_fields = ('created_at',)
    ordering = ('district', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('district', 'name')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# =====================================================================
# Property and PropertyImage Admin
# =====================================================================

class PropertyImageInline(admin.TabularInline):
    """Inline admin for PropertyImage within Property."""
    
    model = PropertyImage
    extra = 1
    fields = ('title', 'image', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin interface for Property model."""
    
    list_display = ('title', 'landlord', 'district', 'rent', 'status', 'created_at')
    list_filter = ('status', 'district__state', 'district', 'created_at')
    search_fields = ('title', 'description', 'landlord__username', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Landlord Information', {
            'fields': ('landlord',)
        }),
        ('Basic Information', {
            'fields': ('title', 'description', 'rent', 'status')
        }),
        ('Location Details', {
            'fields': ('address', 'state', 'district', 'area')
        }),
        ('Geographic Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': 'Latitude: -90 to 90, Longitude: -180 to 180'
        }),
        ('Image', {
            'fields': ('featured_image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('landlord', 'state', 'district', 'area')


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Admin interface for PropertyImage model."""
    
    list_display = ('title', 'property', 'uploaded_at')
    list_filter = ('property__district', 'uploaded_at')
    search_fields = ('title', 'property__title')
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        ('Image Information', {
            'fields': ('property', 'title', 'image')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )


# =====================================================================
# User Search History Admin
# =====================================================================

@admin.register(UserSearchHistory)
class UserSearchHistoryAdmin(admin.ModelAdmin):
    """Admin interface for UserSearchHistory model."""
    
    list_display = ('user', 'search_query', 'district', 'min_rent', 'max_rent', 'timestamp')
    list_filter = ('district__state', 'district', 'timestamp')
    search_fields = ('user__username', 'search_query', 'district__name')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'timestamp')
        }),
        ('Search Query', {
            'fields': ('search_query',)
        }),
        ('Location Filters', {
            'fields': ('state', 'district', 'area')
        }),
        ('Rent Filters', {
            'fields': ('min_rent', 'max_rent')
        }),
        ('Viewed Property', {
            'fields': ('viewed_property',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'state', 'district', 'area', 'viewed_property')
