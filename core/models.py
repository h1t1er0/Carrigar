from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os

def order_file_upload_path(instance, filename):
    """Generate custom file path with customer name and order ID"""
    # Get file extension
    ext = filename.split('.')[-1]
    
    # Get customer name (from user or contact name)
    if instance.order.user:
        customer_name = f"{instance.order.user.first_name}_{instance.order.user.last_name}".strip()
        if not customer_name:
            customer_name = instance.order.user.username
    else:
        customer_name = instance.order.contact_name or "Anonymous"
    
    # Clean customer name (remove special characters, replace spaces with underscores)
    customer_name = "".join(c for c in customer_name if c.isalnum() or c in (' ', '-', '_')).strip()
    customer_name = customer_name.replace(' ', '_')
    
    # Generate filename: CustomerName_OrderID_OriginalName.ext
    new_filename = f"{customer_name}_{instance.order.order_id}_{filename}"
    
    # Return path with date structure
    return f'order_files/{timezone.now().strftime("%Y/%m/%d")}/{new_filename}'

class Order(models.Model):
    ORDER_TYPES = [
        ('small', 'Small Order'),
        ('bulk', 'Bulk Order'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('quoted', 'Quote Sent'),
        ('confirmed', 'Confirmed'),
        ('in_production', 'In Production'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    project_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Contact Information
    contact_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    
    # Order Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps and completion tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expected_completion_date = models.DateField(null=True, blank=True, help_text='Expected completion date for this order')
    actual_completion_date = models.DateField(null=True, blank=True, help_text='Actual completion date when status changed to completed')
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        if not self.project_number and self.order_type == 'small':
            self.project_number = f"CARR{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)
    
    def is_on_time(self):
        """Check if order was completed on time"""
        if not self.expected_completion_date or not self.actual_completion_date:
            return None  # Cannot determine without both dates
        return self.actual_completion_date <= self.expected_completion_date
    
    def is_otif_eligible(self):
        """Check if order is eligible for OTIF calculation (completed with both dates)"""
        return (self.status == 'completed' and 
                self.expected_completion_date and 
                self.actual_completion_date)
    
    def __str__(self):
        return f"{self.order_id} - {self.get_order_type_display()} - {self.status}"

class OrderItem(models.Model):
    SERVICE_CHOICES = [
        ('tube_laser', 'Tube Laser Cutting'),
        ('sheet_laser', 'Sheet Laser Cutting'),
        ('cnc_machining', 'CNC Machining'),
        ('vmc_machining', 'VMC Machining'),
        ('3d_printing', '3D Printing'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order.order_id} - {self.get_service_type_display()}"

class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=order_file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.original_filename:
            self.original_filename = self.file.name.split('/')[-1]
        if not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order.order_id} - {self.original_filename}"

class ProjectManager(models.Model):
    """Model for Carrigar project managers who handle order management"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, default='Operations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class OrderUpdate(models.Model):
    """Model for tracking order progress updates by project managers"""
    UPDATE_TYPES = [
        ('status_change', 'Status Change'),
        ('note', 'General Note'),
        ('quote_sent', 'Quote Sent'),
        ('customer_response', 'Customer Response'),
        ('production_update', 'Production Update'),
        ('delivery_update', 'Delivery Update'),
        ('issue', 'Issue/Problem'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.CASCADE)
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default='note')
    title = models.CharField(max_length=200)
    description = models.TextField()
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    is_customer_visible = models.BooleanField(default=False, help_text='Should customer see this update?')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_id} - {self.title}"

class Vendor(models.Model):
    """Model for manufacturing vendors/suppliers"""
    VENDOR_TYPES = [
        ('tube_laser', 'Tube Laser Cutting'),
        ('sheet_laser', 'Sheet Laser Cutting'),
        ('cnc_machining', 'CNC Machining'),
        ('vmc_machining', 'VMC Machining'),
        ('3d_printing', '3D Printing'),
        ('multi_service', 'Multi-Service'),
    ]
    
    VENDOR_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_hold', 'On Hold'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    vendor_code = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    # Vendor capabilities
    primary_service = models.CharField(max_length=20, choices=VENDOR_TYPES)
    secondary_services = models.CharField(max_length=200, blank=True, help_text='Comma-separated list of other services')
    
    # Machine/Equipment details
    has_tube_laser = models.BooleanField(default=False, help_text='Has tube laser cutting capability')
    tube_laser_details = models.TextField(blank=True, help_text='Tube laser machine details, capacity, etc.')
    
    has_sheet_laser = models.BooleanField(default=False, help_text='Has sheet laser cutting capability')
    sheet_laser_details = models.TextField(blank=True, help_text='Sheet laser machine details, capacity, etc.')
    
    has_cnc_machining = models.BooleanField(default=False, help_text='Has CNC machining capability')
    cnc_machining_details = models.TextField(blank=True, help_text='CNC machine details, capacity, etc.')
    
    has_vmc_machining = models.BooleanField(default=False, help_text='Has VMC machining capability')
    vmc_machining_details = models.TextField(blank=True, help_text='VMC machine details, capacity, etc.')
    
    has_3d_printing = models.BooleanField(default=False, help_text='Has 3D printing capability')
    printing_3d_details = models.TextField(blank=True, help_text='3D printer details, materials, etc.')
    
    # Additional capabilities
    max_material_thickness = models.CharField(max_length=50, blank=True, help_text='Maximum material thickness (e.g., 25mm steel)')
    material_types = models.TextField(blank=True, help_text='Types of materials handled (steel, aluminum, etc.)')
    production_capacity = models.TextField(blank=True, help_text='Daily/monthly production capacity')
    quality_certifications = models.TextField(blank=True, help_text='ISO, quality certifications, etc.')
    
    # Business details
    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    
    # Performance tracking
    status = models.CharField(max_length=20, choices=VENDOR_STATUS, default='active')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text='Overall rating out of 5')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(ProjectManager, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.vendor_code} - {self.company_name}"
    
    def calculate_otif_percentage(self):
        """Calculate OTIF percentage for this vendor"""
        assignments = self.assignments.filter(order__status='completed')
        if not assignments.exists():
            return 0.0
        
        on_time_in_full = assignments.filter(
            is_on_time=True,
            is_in_full=True
        ).count()
        
        return round((on_time_in_full / assignments.count()) * 100, 2)
    
    def get_total_orders(self):
        """Get total number of orders assigned to this vendor"""
        return self.assignments.count()
    
    def get_completed_orders(self):
        """Get number of completed orders"""
        return self.assignments.filter(order__status='completed').count()
    
    def get_capabilities(self):
        """Get list of vendor's manufacturing capabilities"""
        capabilities = []
        if self.has_tube_laser:
            capabilities.append({'name': 'Tube Laser Cutting', 'details': self.tube_laser_details})
        if self.has_sheet_laser:
            capabilities.append({'name': 'Sheet Laser Cutting', 'details': self.sheet_laser_details})
        if self.has_cnc_machining:
            capabilities.append({'name': 'CNC Machining', 'details': self.cnc_machining_details})
        if self.has_vmc_machining:
            capabilities.append({'name': 'VMC Machining', 'details': self.vmc_machining_details})
        if self.has_3d_printing:
            capabilities.append({'name': '3D Printing', 'details': self.printing_3d_details})
        return capabilities

class VendorAssignment(models.Model):
    """Model to track which vendor is assigned to which order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='vendor_assignments')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(ProjectManager, on_delete=models.CASCADE)
    
    # Assignment details
    assigned_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    dispatch_date = models.DateField(null=True, blank=True)
    
    # OTIF tracking
    is_on_time = models.BooleanField(default=False, help_text='Was delivery on time?')
    is_in_full = models.BooleanField(default=False, help_text='Was delivery complete?')
    delivery_notes = models.TextField(blank=True)
    
    # Quality and performance
    quality_rating = models.IntegerField(
        choices=[(i, f'{i} Star') for i in range(1, 6)],
        null=True, blank=True,
        help_text='Quality rating from 1-5 stars'
    )
    
    class Meta:
        unique_together = ['order', 'vendor']  # One vendor per order for now
    
    def __str__(self):
        return f"{self.order.order_id} → {self.vendor.vendor_code}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate OTIF when delivery is marked
        if self.actual_delivery_date and self.expected_delivery_date:
            self.is_on_time = self.actual_delivery_date <= self.expected_delivery_date
        super().save(*args, **kwargs)
    
    def get_delivery_status(self):
        """Get human-readable delivery status"""
        if not self.actual_delivery_date:
            if self.expected_delivery_date and timezone.now().date() > self.expected_delivery_date:
                return 'Overdue'
            return 'Pending'
        elif self.is_on_time and self.is_in_full:
            return 'OTIF'
        elif self.is_on_time:
            return 'On Time'
        elif self.is_in_full:
            return 'In Full'
        else:
            return 'Late/Incomplete'