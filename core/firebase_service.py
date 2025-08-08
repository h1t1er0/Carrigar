import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

class FirebaseService:
    """
    Firebase service for handling all database operations
    """
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                # Try to get credentials from environment variable (for production)
                firebase_config = os.environ.get('FIREBASE_CONFIG')
                if firebase_config:
                    try:
                        cred_dict = json.loads(firebase_config)
                        cred = credentials.Certificate(cred_dict)
                        print("Using Firebase credentials from environment variable")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing FIREBASE_CONFIG JSON: {e}")
                        raise
                else:
                    # Fallback to local file (for development)
                    from django.conf import settings
                    cred_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')
                    if os.path.exists(cred_path):
                        cred = credentials.Certificate(cred_path)
                        print("Using Firebase credentials from local file")
                    else:
                        raise FileNotFoundError("Firebase credentials not found. Please set FIREBASE_CONFIG environment variable or provide firebase_credentials.json file.")
                
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("Firebase initialized successfully")
            except Exception as e:
                print(f"Error initializing Firebase: {e}")
                raise
    
    @property
    def db(self):
        """Get Firestore database instance"""
        if self._db is None:
            self._initialize_firebase()
        return self._db
    
    # User Operations
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            user_id = str(uuid.uuid4())
            user_data.update({
                'id': user_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.db.collection('users').document(user_id).set(user_data)
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            users = self.db.collection('users').where('email', '==', email).limit(1).get()
            for user in users:
                return user.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.now()
            self.db.collection('users').document(user_id).update(update_data)
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            self.db.collection('users').document(user_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # Order Operations
    def create_order(self, order_data: Dict[str, Any]) -> str:
        """Create a new order"""
        try:
            order_id = str(uuid.uuid4())
            order_data.update({
                'id': order_id,
                'status': 'pending',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.db.collection('orders').document(order_id).set(order_data)
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            raise
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        try:
            doc = self.db.collection('orders').document(order_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting order: {e}")
            return None
    
    def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a user"""
        try:
            orders = self.db.collection('orders').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).get()
            return [order.to_dict() for order in orders]
        except Exception as e:
            print(f"Error getting user orders: {e}")
            return []
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        try:
            self.db.collection('orders').document(order_id).update({
                'status': status,
                'updated_at': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders (admin function)"""
        try:
            orders = self.db.collection('orders').order_by('created_at', direction=firestore.Query.DESCENDING).get()
            return [order.to_dict() for order in orders]
        except Exception as e:
            print(f"Error getting all orders: {e}")
            return []
    
    # Service Operations
    def create_service(self, service_data: Dict[str, Any]) -> str:
        """Create a new service"""
        try:
            service_id = str(uuid.uuid4())
            service_data.update({
                'id': service_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.db.collection('services').document(service_id).set(service_data)
            return service_id
        except Exception as e:
            print(f"Error creating service: {e}")
            raise
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services"""
        try:
            services = self.db.collection('services').get()
            return [service.to_dict() for service in services]
        except Exception as e:
            print(f"Error getting services: {e}")
            return []
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        try:
            doc = self.db.collection('services').document(service_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting service: {e}")
            return None
    
    # Generic CRUD Operations
    def create_document(self, collection: str, data: Dict[str, Any], doc_id: str = None) -> str:
        """Create a document in any collection"""
        try:
            if not doc_id:
                doc_id = str(uuid.uuid4())
            
            data.update({
                'id': doc_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.db.collection(collection).document(doc_id).set(data)
            return doc_id
        except Exception as e:
            print(f"Error creating document in {collection}: {e}")
            raise
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from any collection"""
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting document from {collection}: {e}")
            return None
    
    def update_document(self, collection: str, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document in any collection"""
        try:
            update_data['updated_at'] = datetime.now()
            self.db.collection(collection).document(doc_id).update(update_data)
            return True
        except Exception as e:
            print(f"Error updating document in {collection}: {e}")
            return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from any collection"""
        try:
            self.db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting document from {collection}: {e}")
            return False
    
    def get_collection(self, collection: str, limit: int = None, order_by: str = None) -> List[Dict[str, Any]]:
        """Get all documents from a collection"""
        try:
            query = self.db.collection(collection)
            
            if order_by:
                query = query.order_by(order_by, direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.get()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Error getting collection {collection}: {e}")
            return []


# Create a global instance
firebase_service = FirebaseService()
