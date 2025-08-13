from django.contrib import admin

# Register your models here.
from core.models import Order, OrderItem, OrderFile, ProjectManager, OrderUpdate, Vendor, VendorAssignment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'contact_name', 'order_type', 'status', 'created_at']
    list_filter = ['status', 'order_type', 'created_at']
    search_fields = ['order_id', 'contact_name', 'contact_email', 'company_name']
    readonly_fields = ['order_id', 'created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'service_type', 'quantity', 'unit_price', 'total_price']
    list_filter = ['service_type']
    search_fields = ['order__order_id', 'description']

@admin.register(OrderFile)
class OrderFileAdmin(admin.ModelAdmin):
    list_display = ['order', 'original_filename', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at', 'file_type']
    search_fields = ['order__order_id', 'original_filename']

@admin.register(ProjectManager)
class ProjectManagerAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']

@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ['order', 'project_manager', 'update_type', 'title', 'is_customer_visible', 'created_at']
    list_filter = ['update_type', 'is_customer_visible', 'created_at']
    search_fields = ['order__order_id', 'title', 'description']
    readonly_fields = ['created_at']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'company_name', 'primary_service', 'status', 'rating', 'created_at']
    list_filter = ['primary_service', 'status', 'created_at']
    search_fields = ['vendor_code', 'company_name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor_code', 'company_name', 'contact_person', 'email', 'phone', 'address')
        }),
        ('Services', {
            'fields': ('primary_service', 'secondary_services')
        }),
        ('Machine Capabilities', {
            'fields': (
                ('has_tube_laser', 'tube_laser_details'),
                ('has_sheet_laser', 'sheet_laser_details'),
                ('has_cnc_machining', 'cnc_machining_details'),
                ('has_vmc_machining', 'vmc_machining_details'),
                ('has_3d_printing', 'printing_3d_details'),
            )
        }),
        ('Technical Specifications', {
            'fields': ('max_material_thickness', 'material_types', 'production_capacity', 'quality_certifications'),
            'classes': ('collapse',)
        }),
        ('Business Details', {
            'fields': ('gst_number', 'pan_number')
        }),
        ('Performance', {
            'fields': ('status', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(VendorAssignment)
class VendorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'vendor', 'assigned_by', 'expected_delivery_date', 'actual_delivery_date', 'get_delivery_status', 'quality_rating']
    list_filter = ['assigned_date', 'is_on_time', 'is_in_full', 'quality_rating']
    search_fields = ['order__order_id', 'vendor__company_name', 'vendor__vendor_code']
    readonly_fields = ['assigned_date', 'is_on_time']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('order', 'vendor', 'assigned_by', 'assigned_date')
        }),
        ('Delivery Schedule', {
            'fields': ('expected_delivery_date', 'actual_delivery_date', 'dispatch_date')
        }),
        ('Performance Tracking', {
            'fields': ('is_on_time', 'is_in_full', 'quality_rating', 'delivery_notes')
        })
    )
