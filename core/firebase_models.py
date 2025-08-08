from typing import Dict, List, Optional, Any
from datetime import datetime
from .firebase_service import firebase_service

class FirebaseUser:
    """Firebase-based User model"""
    
    def __init__(self, data: Dict[str, Any] = None):
        if data:
            self.id = data.get('id')
            self.username = data.get('username')
            self.email = data.get('email')
            self.first_name = data.get('first_name', '')
            self.last_name = data.get('last_name', '')
            self.phone = data.get('phone', '')
            self.is_vendor = data.get('is_vendor', False)
            self.google_id = data.get('google_id')
            self.profile_picture = data.get('profile_picture', '')
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')
        else:
            self.id = None
            self.username = None
            self.email = None
            self.first_name = ''
            self.last_name = ''
            self.phone = ''
            self.is_vendor = False
            self.google_id = None
            self.profile_picture = ''
            self.created_at = None
            self.updated_at = None
    
    def save(self) -> str:
        """Save user to Firebase"""
        user_data = {
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_vendor': self.is_vendor,
            'google_id': self.google_id,
            'profile_picture': self.profile_picture
        }
        
        if self.id:
            # Update existing user
            firebase_service.update_user(self.id, user_data)
            return self.id
        else:
            # Create new user
            self.id = firebase_service.create_user(user_data)
            return self.id
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['FirebaseUser']:
        """Get user by ID"""
        user_data = firebase_service.get_user(user_id)
        if user_data:
            return cls(user_data)
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['FirebaseUser']:
        """Get user by email"""
        user_data = firebase_service.get_user_by_email(email)
        if user_data:
            return cls(user_data)
        return None
    
    @classmethod
    def create_user(cls, username: str, email: str, **kwargs) -> 'FirebaseUser':
        """Create a new user"""
        user = cls()
        user.username = username
        user.email = email
        user.first_name = kwargs.get('first_name', '')
        user.last_name = kwargs.get('last_name', '')
        user.phone = kwargs.get('phone', '')
        user.is_vendor = kwargs.get('is_vendor', False)
        user.google_id = kwargs.get('google_id')
        user.profile_picture = kwargs.get('profile_picture', '')
        user.save()
        return user
    
    def delete(self) -> bool:
        """Delete user"""
        if self.id:
            return firebase_service.delete_user(self.id)
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_vendor': self.is_vendor,
            'google_id': self.google_id,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}".strip()


class FirebaseOrder:
    """Firebase-based Order model"""
    
    def __init__(self, data: Dict[str, Any] = None):
        if data:
            self.id = data.get('id')
            self.user_id = data.get('user_id')
            self.service_type = data.get('service_type')
            self.description = data.get('description', '')
            self.pickup_location = data.get('pickup_location', '')
            self.delivery_location = data.get('delivery_location', '')
            self.pickup_date = data.get('pickup_date')
            self.delivery_date = data.get('delivery_date')
            self.price = data.get('price', 0.0)
            self.status = data.get('status', 'pending')
            self.vendor_id = data.get('vendor_id')
            self.special_instructions = data.get('special_instructions', '')
            self.contact_phone = data.get('contact_phone', '')
            self.file_url = data.get('file_url', '')
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')
        else:
            self.id = None
            self.user_id = None
            self.service_type = None
            self.description = ''
            self.pickup_location = ''
            self.delivery_location = ''
            self.pickup_date = None
            self.delivery_date = None
            self.price = 0.0
            self.status = 'pending'
            self.vendor_id = None
            self.special_instructions = ''
            self.contact_phone = ''
            self.file_url = ''
            self.created_at = None
            self.updated_at = None
    
    def save(self) -> str:
        """Save order to Firebase"""
        order_data = {
            'user_id': self.user_id,
            'service_type': self.service_type,
            'description': self.description,
            'pickup_location': self.pickup_location,
            'delivery_location': self.delivery_location,
            'pickup_date': self.pickup_date,
            'delivery_date': self.delivery_date,
            'price': self.price,
            'status': self.status,
            'vendor_id': self.vendor_id,
            'special_instructions': self.special_instructions,
            'contact_phone': self.contact_phone,
            'file_url': self.file_url
        }
        
        if self.id:
            # Update existing order
            firebase_service.update_document('orders', self.id, order_data)
            return self.id
        else:
            # Create new order
            self.id = firebase_service.create_order(order_data)
            return self.id
    
    @classmethod
    def get_by_id(cls, order_id: str) -> Optional['FirebaseOrder']:
        """Get order by ID"""
        order_data = firebase_service.get_order(order_id)
        if order_data:
            return cls(order_data)
        return None
    
    @classmethod
    def get_user_orders(cls, user_id: str) -> List['FirebaseOrder']:
        """Get all orders for a user"""
        orders_data = firebase_service.get_user_orders(user_id)
        return [cls(order_data) for order_data in orders_data]
    
    @classmethod
    def get_all_orders(cls) -> List['FirebaseOrder']:
        """Get all orders"""
        orders_data = firebase_service.get_all_orders()
        return [cls(order_data) for order_data in orders_data]
    
    @classmethod
    def create_order(cls, user_id: str, service_type: str, **kwargs) -> 'FirebaseOrder':
        """Create a new order"""
        order = cls()
        order.user_id = user_id
        order.service_type = service_type
        order.description = kwargs.get('description', '')
        order.pickup_location = kwargs.get('pickup_location', '')
        order.delivery_location = kwargs.get('delivery_location', '')
        order.pickup_date = kwargs.get('pickup_date')
        order.delivery_date = kwargs.get('delivery_date')
        order.price = kwargs.get('price', 0.0)
        order.special_instructions = kwargs.get('special_instructions', '')
        order.contact_phone = kwargs.get('contact_phone', '')
        order.file_url = kwargs.get('file_url', '')
        order.save()
        return order
    
    def update_status(self, status: str) -> bool:
        """Update order status"""
        self.status = status
        return firebase_service.update_order_status(self.id, status)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_type': self.service_type,
            'description': self.description,
            'pickup_location': self.pickup_location,
            'delivery_location': self.delivery_location,
            'pickup_date': self.pickup_date,
            'delivery_date': self.delivery_date,
            'price': self.price,
            'status': self.status,
            'vendor_id': self.vendor_id,
            'special_instructions': self.special_instructions,
            'contact_phone': self.contact_phone,
            'file_url': self.file_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class FirebaseService:
    """Firebase-based Service model"""
    
    def __init__(self, data: Dict[str, Any] = None):
        if data:
            self.id = data.get('id')
            self.name = data.get('name')
            self.description = data.get('description', '')
            self.category = data.get('category', '')
            self.base_price = data.get('base_price', 0.0)
            self.is_active = data.get('is_active', True)
            self.icon = data.get('icon', '')
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')
        else:
            self.id = None
            self.name = None
            self.description = ''
            self.category = ''
            self.base_price = 0.0
            self.is_active = True
            self.icon = ''
            self.created_at = None
            self.updated_at = None
    
    def save(self) -> str:
        """Save service to Firebase"""
        service_data = {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'base_price': self.base_price,
            'is_active': self.is_active,
            'icon': self.icon
        }
        
        if self.id:
            # Update existing service
            firebase_service.update_document('services', self.id, service_data)
            return self.id
        else:
            # Create new service
            self.id = firebase_service.create_service(service_data)
            return self.id
    
    @classmethod
    def get_by_id(cls, service_id: str) -> Optional['FirebaseService']:
        """Get service by ID"""
        service_data = firebase_service.get_service(service_id)
        if service_data:
            return cls(service_data)
        return None
    
    @classmethod
    def get_all_services(cls) -> List['FirebaseService']:
        """Get all active services"""
        services_data = firebase_service.get_all_services()
        return [cls(service_data) for service_data in services_data if service_data.get('is_active', True)]
    
    @classmethod
    def create_service(cls, name: str, **kwargs) -> 'FirebaseService':
        """Create a new service"""
        service = cls()
        service.name = name
        service.description = kwargs.get('description', '')
        service.category = kwargs.get('category', '')
        service.base_price = kwargs.get('base_price', 0.0)
        service.is_active = kwargs.get('is_active', True)
        service.icon = kwargs.get('icon', '')
        service.save()
        return service
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'base_price': self.base_price,
            'is_active': self.is_active,
            'icon': self.icon,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
