from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, OrderFile
import json

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
        
        # Check authentication for bulk orders
        if order_type == 'bulk' and not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Login required for bulk orders',
                'require_login': True
            }, status=401)
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_type=order_type,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
        )
        
        # Create order item
        if service_type:
            service_mapping = {
                'Tube Laser Cutting': 'tube_laser',
                'Sheet Laser Cutting': 'sheet_laser',
                'CNC Machining': 'cnc_machining',
                'VMC Machining': 'vmc_machining',
                '3D Printing': '3d_printing',
            }
            
            OrderItem.objects.create(
                order=order,
                service_type=service_mapping.get(service_type, 'tube_laser'),
                description=f"Order for {service_type}"
            )
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'project_number': order.project_number,
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
        
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
        
        # Create order file
        order_file = OrderFile.objects.create(
            order=order,
            file=file,
            original_filename=file.name,
            file_type=file.content_type,
            file_size=file.size
        )
        
        return JsonResponse({
            'success': True,
            'file_id': order_file.id,
            'filename': order_file.original_filename,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def my_orders(request):
    """View user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/my_orders.html', {'orders': orders})

def order_status(request, order_id):
    """Get order status by order ID or project number"""
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        try:
            order = Order.objects.get(project_number=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
    
    return JsonResponse({
        'success': True,
        'order': {
            'order_id': order.order_id,
            'project_number': order.project_number,
            'status': order.status,
            'order_type': order.order_type,
            'created_at': order.created_at.isoformat(),
            'items': [{
                'service_type': item.get_service_type_display(),
                'description': item.description
            } for item in order.items.all()]
        }
    })
