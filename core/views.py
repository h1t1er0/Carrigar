from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .firebase_models import FirebaseUser, FirebaseOrder, FirebaseService
from .firebase_service import firebase_service
import json
import uuid
from datetime import datetime

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def services(request):
    return render(request, 'core/services.html')

def how_it_works(request):
    return render(request, 'core/how_it_works.html')

def become_vendor(request):
    return render(request, 'core/become_vendor.html')

@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    """Create a new order from the guided form"""
    try:
        data = json.loads(request.body)
        
        # Extract order data
        order_type = data.get('order_type', 'small')
        service_type = data.get('service_type')
        contact_name = data.get('contact_name', '')
        contact_email = data.get('contact_email', '')
        contact_phone = data.get('contact_phone', '')
        pickup_location = data.get('pickup_location', '')
        delivery_location = data.get('delivery_location', '')
        special_instructions = data.get('special_instructions', '')
        
        # Check authentication for bulk orders
        if order_type == 'bulk' and not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Login required for bulk orders',
                'require_login': True
            }, status=401)
        
        # Get user ID if authenticated
        user_id = None
        if request.user.is_authenticated:
            # Try to get Firebase user or create one
            firebase_user = FirebaseUser.get_by_email(request.user.email)
            if not firebase_user:
                firebase_user = FirebaseUser.create_user(
                    username=request.user.username,
                    email=request.user.email,
                    first_name=getattr(request.user, 'first_name', ''),
                    last_name=getattr(request.user, 'last_name', '')
                )
            user_id = firebase_user.id
        
        # Service type mapping
        service_mapping = {
            'Tube Laser Cutting': 'tube_laser',
            'Sheet Laser Cutting': 'sheet_laser',
            'CNC Machining': 'cnc_machining',
            'VMC Machining': 'vmc_machining',
            '3D Printing': '3d_printing',
        }
        
        # Create Firebase order
        order = FirebaseOrder.create_order(
            user_id=user_id,
            service_type=service_mapping.get(service_type, 'tube_laser'),
            description=f"Order for {service_type}",
            pickup_location=pickup_location,
            delivery_location=delivery_location,
            contact_phone=contact_phone,
            special_instructions=special_instructions
        )
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Order created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Handle file upload for orders"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        order_id = request.POST.get('order_id')
        
        if not order_id:
            return JsonResponse({'success': False, 'message': 'Order ID required'}, status=400)
        
        # Get Firebase order
        order = FirebaseOrder.get_by_id(order_id)
        if not order:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
        
        # For now, we'll store the file locally and save the path
        # In a production environment, you'd want to upload to Firebase Storage or similar
        import os
        from django.conf import settings
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Update order with file URL
        file_url = f"/media/uploads/{unique_filename}"
        firebase_service.update_document('orders', order_id, {'file_url': file_url})
        
        return JsonResponse({
            'success': True,
            'file_url': file_url,
            'filename': file.name,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def my_orders(request):
    """View user's orders"""
    # Get Firebase user
    firebase_user = FirebaseUser.get_by_email(request.user.email)
    orders = []
    
    if firebase_user:
        orders = FirebaseOrder.get_user_orders(firebase_user.id)
    
    return render(request, 'core/my_orders.html', {'orders': orders})

def order_status(request, order_id):
    """Get order status by order ID"""
    order = FirebaseOrder.get_by_id(order_id)
    
    if not order:
        return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
    
    return JsonResponse({
        'success': True,
        'order': {
            'id': order.id,
            'service_type': order.service_type,
            'status': order.status,
            'description': order.description,
            'pickup_location': order.pickup_location,
            'delivery_location': order.delivery_location,
            'contact_phone': order.contact_phone,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'special_instructions': order.special_instructions,
            'file_url': order.file_url
        }
    })
