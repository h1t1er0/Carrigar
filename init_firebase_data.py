#!/usr/bin/env python
"""
Initialize Firebase with default data
Run this script to populate Firebase with initial services and data
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')
django.setup()

from core.firebase_models import FirebaseService

def initialize_services():
    """Initialize default services in Firebase"""
    
    default_services = [
        {
            'name': 'Tube Laser Cutting',
            'description': 'Precision tube laser cutting services for various materials',
            'category': 'Laser Cutting',
            'base_price': 50.0,
            'icon': '🔥'
        },
        {
            'name': 'Sheet Laser Cutting',
            'description': 'High-quality sheet laser cutting for metal fabrication',
            'category': 'Laser Cutting',
            'base_price': 40.0,
            'icon': '⚡'
        },
        {
            'name': 'CNC Machining',
            'description': 'Computer-controlled machining for precise parts',
            'category': 'Machining',
            'base_price': 75.0,
            'icon': '⚙️'
        },
        {
            'name': 'VMC Machining',
            'description': 'Vertical machining center services',
            'category': 'Machining',
            'base_price': 80.0,
            'icon': '🔧'
        },
        {
            'name': '3D Printing',
            'description': 'Additive manufacturing and rapid prototyping',
            'category': '3D Printing',
            'base_price': 30.0,
            'icon': '🖨️'
        }
    ]
    
    print("Initializing services in Firebase...")
    
    for service_data in default_services:
        try:
            service = FirebaseService.create_service(**service_data)
            print(f"✅ Created service: {service_data['name']} (ID: {service.id})")
        except Exception as e:
            print(f"❌ Error creating service {service_data['name']}: {e}")
    
    print("Service initialization complete!")

if __name__ == "__main__":
    initialize_services()
