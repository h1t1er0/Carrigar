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
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        if not self.project_number and self.order_type == 'small':
            self.project_number = f"CARR{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)
    
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
