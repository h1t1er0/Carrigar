from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Order, OrderUpdate, ProjectManager, OrderItem, OrderFile, Vendor, VendorAssignment
import json
from datetime import datetime, timedelta
from .crm_views_vendor import crm_vendor_create, crm_vendor_edit, crm_set_expected_date, crm_set_actual_date

def is_project_manager(user):
    """Check if user is a project manager"""
    try:
        return hasattr(user, 'projectmanager') and user.projectmanager.is_active
    except:
        return False

@login_required
def crm_dashboard(request):
    """Main CRM dashboard for project managers"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    # Get dashboard statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    in_review_orders = Order.objects.filter(status='reviewing').count()
    in_production_orders = Order.objects.filter(status='in_production').count()
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').prefetch_related('items', 'files').order_by('-created_at')[:10]
    
    # Orders by status for chart
    status_counts = Order.objects.values('status').annotate(count=Count('status'))
    
    # Recent updates by this project manager
    pm = request.user.projectmanager
    recent_updates = OrderUpdate.objects.filter(project_manager=pm).select_related('order')[:5]
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'in_review_orders': in_review_orders,
        'in_production_orders': in_production_orders,
        'recent_orders': recent_orders,
        'status_counts': list(status_counts),
        'recent_updates': recent_updates,
        'project_manager': pm,
    }
    
    return render(request, 'core/crm/dashboard.html', context)

@login_required
def crm_orders(request):
    """Orders list view with filters and search"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    order_type_filter = request.GET.get('order_type', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    orders = Order.objects.select_related('user').prefetch_related('items', 'files', 'updates').order_by('-created_at')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if order_type_filter:
        orders = orders.filter(order_type=order_type_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(contact_name__icontains=search_query) |
            Q(contact_email__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(project_number__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(orders, 20)  # Show 20 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'order_type_filter': order_type_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'order_status_choices': Order.STATUS_CHOICES,
        'order_type_choices': Order.ORDER_TYPES,
    }
    
    return render(request, 'core/crm/orders.html', context)

@login_required
def crm_order_detail(request, order_id):
    """Detailed view of a specific order"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    order = get_object_or_404(Order, order_id=order_id)
    updates = order.updates.select_related('project_manager__user').order_by('-created_at')
    
    # Get current vendor assignment
    current_assignment = order.vendor_assignments.first()
    
    # Get available vendors for assignment
    available_vendors = Vendor.objects.filter(status='active').order_by('company_name')
    
    context = {
        'order': order,
        'updates': updates,
        'current_assignment': current_assignment,
        'available_vendors': available_vendors,
        'status_choices': Order.STATUS_CHOICES,
        'update_types': OrderUpdate.UPDATE_TYPES,
    }
    
    return render(request, 'core/crm/order_detail.html', context)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crm_update_order_status(request):
    """Update order status"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('new_status')
        update_title = data.get('title', '')
        update_description = data.get('description', '')
        
        order = get_object_or_404(Order, order_id=order_id)
        old_status = order.status
        
        # Update order status
        order.status = new_status
        
        # If status is being changed to completed, set actual completion date
        if new_status == 'completed' and old_status != 'completed':
            order.actual_completion_date = timezone.now().date()
        
        order.save()
        
        # Create update record
        OrderUpdate.objects.create(
            order=order,
            project_manager=request.user.projectmanager,
            update_type='status_change',
            title=update_title or f'Status changed to {order.get_status_display()}',
            description=update_description or f'Order status updated from {dict(Order.STATUS_CHOICES)[old_status]} to {order.get_status_display()}',
            old_status=old_status,
            new_status=new_status,
            is_customer_visible=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Order status updated successfully',
            'new_status': new_status,
            'new_status_display': order.get_status_display()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crm_add_order_update(request):
    """Add a new update to an order"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        update_type = data.get('update_type', 'note')
        title = data.get('title', '')
        description = data.get('description', '')
        is_customer_visible = data.get('is_customer_visible', False)
        
        order = get_object_or_404(Order, order_id=order_id)
        
        # Create update record
        update = OrderUpdate.objects.create(
            order=order,
            project_manager=request.user.projectmanager,
            update_type=update_type,
            title=title,
            description=description,
            is_customer_visible=is_customer_visible
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Update added successfully',
            'update_id': update.id,
            'created_at': update.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def crm_analytics(request):
    """Analytics and reports for project managers"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    # Date range for analytics (default to last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Orders by status
    status_data = []
    for status, display in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status).count()
        status_data.append({'status': display, 'count': count})
    
    # Orders by service type
    service_data = []
    for service, display in OrderItem.SERVICE_CHOICES:
        count = OrderItem.objects.filter(service_type=service).count()
        service_data.append({'service': display, 'count': count})
    
    # Orders over time (last 30 days)
    orders_timeline = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        count = Order.objects.filter(created_at__date=date).count()
        orders_timeline.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    # Top customers (by order count)
    top_customers = Order.objects.filter(user__isnull=False)\
        .values('user__email', 'user__first_name', 'user__last_name')\
        .annotate(order_count=Count('id'))\
        .order_by('-order_count')[:10]
    
    # OTIF Performance - based on order completion dates
    completed_orders = Order.objects.filter(status='completed')
    otif_eligible_orders = completed_orders.filter(
        expected_completion_date__isnull=False,
        actual_completion_date__isnull=False
    )
    on_time_orders = otif_eligible_orders.filter(
        actual_completion_date__lte=F('expected_completion_date')
    )
    overall_otif = (on_time_orders.count() / otif_eligible_orders.count() * 100) if otif_eligible_orders.exists() else 0
    
    # Vendor performance
    vendor_performance = []
    for vendor in Vendor.objects.filter(status='active')[:10]:
        vendor_performance.append({
            'vendor': vendor.company_name,
            'otif': vendor.calculate_otif_percentage(),
            'total_orders': vendor.get_total_orders(),
            'completed_orders': vendor.get_completed_orders()
        })
    
    context = {
        'status_data': status_data,
        'service_data': service_data,
        'orders_timeline': orders_timeline,
        'top_customers': top_customers,
        'overall_otif': round(overall_otif, 2),
        'vendor_performance': vendor_performance,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'core/crm/analytics.html', context)

@login_required
def crm_vendors(request):
    """Vendor management view"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    vendors = Vendor.objects.annotate(
        total_orders=Count('assignments'),
        completed_orders=Count('assignments', filter=Q(assignments__order__status='completed'))
    ).order_by('-created_at')
    
    # Apply filters
    if status_filter:
        vendors = vendors.filter(status=status_filter)
    
    if service_filter:
        vendors = vendors.filter(primary_service=service_filter)
    
    if search_query:
        vendors = vendors.filter(
            Q(vendor_code__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'search_query': search_query,
        'vendor_status_choices': Vendor.VENDOR_STATUS,
        'vendor_service_choices': Vendor.VENDOR_TYPES,
    }
    
    return render(request, 'core/crm/vendors.html', context)

@login_required
def crm_vendor_detail(request, vendor_id):
    """Detailed view of a specific vendor"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    assignments = vendor.assignments.select_related('order').order_by('-assigned_date')
    
    # Performance metrics
    total_assignments = assignments.count()
    completed_assignments = assignments.filter(order__status='completed').count()
    otif_assignments = assignments.filter(is_on_time=True, is_in_full=True).count()
    
    context = {
        'vendor': vendor,
        'assignments': assignments,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'otif_assignments': otif_assignments,
        'otif_percentage': vendor.calculate_otif_percentage(),
    }
    
    return render(request, 'core/crm/vendor_detail.html', context)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crm_assign_vendor(request):
    """Assign a vendor to an order"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        vendor_id = data.get('vendor_id')
        expected_delivery_date = data.get('expected_delivery_date')
        
        order = get_object_or_404(Order, order_id=order_id)
        vendor = get_object_or_404(Vendor, id=vendor_id)
        
        # Create or update vendor assignment
        assignment, created = VendorAssignment.objects.get_or_create(
            order=order,
            defaults={
                'vendor': vendor,
                'assigned_by': request.user.projectmanager,
                'expected_delivery_date': expected_delivery_date if expected_delivery_date else None
            }
        )
        
        if not created:
            assignment.vendor = vendor
            assignment.assigned_by = request.user.projectmanager
            if expected_delivery_date:
                assignment.expected_delivery_date = expected_delivery_date
            assignment.save()
        
        # Create update record
        OrderUpdate.objects.create(
            order=order,
            project_manager=request.user.projectmanager,
            update_type='note',
            title=f'Vendor assigned: {vendor.company_name}',
            description=f'Order assigned to vendor {vendor.vendor_code} - {vendor.company_name}',
            is_customer_visible=False
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Order assigned to {vendor.company_name}',
            'assignment_id': assignment.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def crm_update_delivery(request):
    """Update delivery information for a vendor assignment"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        actual_delivery_date = data.get('actual_delivery_date')
        dispatch_date = data.get('dispatch_date')
        is_in_full = data.get('is_in_full', False)
        quality_rating = data.get('quality_rating')
        delivery_notes = data.get('delivery_notes', '')
        
        assignment = get_object_or_404(VendorAssignment, id=assignment_id)
        
        # Update delivery information
        if actual_delivery_date:
            assignment.actual_delivery_date = actual_delivery_date
        if dispatch_date:
            assignment.dispatch_date = dispatch_date
        assignment.is_in_full = is_in_full
        if quality_rating:
            assignment.quality_rating = int(quality_rating)
        assignment.delivery_notes = delivery_notes
        
        assignment.save()  # This will auto-calculate is_on_time
        
        # Create update record
        OrderUpdate.objects.create(
            order=assignment.order,
            project_manager=request.user.projectmanager,
            update_type='delivery_update',
            title='Delivery information updated',
            description=f'Delivery status updated for vendor {assignment.vendor.company_name}. Status: {assignment.get_delivery_status()}',
            is_customer_visible=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Delivery information updated successfully',
            'delivery_status': assignment.get_delivery_status()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
