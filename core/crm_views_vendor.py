from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Vendor, ProjectManager, Order

def is_project_manager(user):
    """Check if user is a project manager"""
    try:
        return hasattr(user, 'projectmanager') and user.projectmanager.is_active
    except:
        return False

@login_required
def crm_vendor_create(request):
    """Create a new vendor"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Generate vendor code
            last_vendor = Vendor.objects.order_by('-id').first()
            if last_vendor:
                last_num = int(last_vendor.vendor_code[3:])  # Extract number from VEN001
                new_num = last_num + 1
            else:
                new_num = 1
            vendor_code = f'VEN{new_num:03d}'
            
            # Create vendor
            vendor = Vendor.objects.create(
                vendor_code=vendor_code,
                company_name=request.POST.get('company_name'),
                contact_person=request.POST.get('contact_person'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                primary_service=request.POST.get('primary_service'),
                secondary_services=request.POST.get('secondary_services', ''),
                gst_number=request.POST.get('gst_number', ''),
                pan_number=request.POST.get('pan_number', ''),
                status=request.POST.get('status', 'active'),
                rating=float(request.POST.get('rating', 0)),
                created_by=request.user.projectmanager,
                # Machine capabilities
                has_tube_laser=request.POST.get('has_tube_laser') == 'on',
                has_sheet_laser=request.POST.get('has_sheet_laser') == 'on',
                has_cnc_machining=request.POST.get('has_cnc_machining') == 'on',
                has_vmc_machining=request.POST.get('has_vmc_machining') == 'on',
                has_3d_printing=request.POST.get('has_3d_printing') == 'on',
                tube_laser_details=request.POST.get('tube_laser_details', ''),
                sheet_laser_details=request.POST.get('sheet_laser_details', ''),
                cnc_machining_details=request.POST.get('cnc_machining_details', ''),
                vmc_machining_details=request.POST.get('vmc_machining_details', ''),
                printing_3d_details=request.POST.get('printing_3d_details', ''),
                max_material_thickness=request.POST.get('max_material_thickness', ''),
                material_types=request.POST.get('material_types', ''),
                production_capacity=request.POST.get('production_capacity', ''),
                quality_certifications=request.POST.get('quality_certifications', ''),
            )
            
            messages.success(request, f'Vendor {vendor.company_name} created successfully!')
            return redirect('crm_vendor_detail', vendor_id=vendor.id)
            
        except Exception as e:
            messages.error(request, f'Error creating vendor: {str(e)}')
    
    context = {
        'vendor_status_choices': Vendor.VENDOR_STATUS,
        'vendor_service_choices': Vendor.VENDOR_TYPES,
    }
    
    return render(request, 'core/crm/vendor_create.html', context)

@login_required
def crm_vendor_edit(request, vendor_id):
    """Edit an existing vendor"""
    if not is_project_manager(request.user):
        messages.error(request, 'Access denied. Project Manager privileges required.')
        return redirect('home')
    
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        try:
            # Update vendor
            vendor.company_name = request.POST.get('company_name')
            vendor.contact_person = request.POST.get('contact_person')
            vendor.email = request.POST.get('email')
            vendor.phone = request.POST.get('phone')
            vendor.address = request.POST.get('address')
            vendor.primary_service = request.POST.get('primary_service')
            vendor.secondary_services = request.POST.get('secondary_services', '')
            vendor.gst_number = request.POST.get('gst_number', '')
            vendor.pan_number = request.POST.get('pan_number', '')
            vendor.status = request.POST.get('status', 'active')
            vendor.rating = float(request.POST.get('rating', 0))
            # Machine capabilities
            vendor.has_tube_laser = request.POST.get('has_tube_laser') == 'on'
            vendor.has_sheet_laser = request.POST.get('has_sheet_laser') == 'on'
            vendor.has_cnc_machining = request.POST.get('has_cnc_machining') == 'on'
            vendor.has_vmc_machining = request.POST.get('has_vmc_machining') == 'on'
            vendor.has_3d_printing = request.POST.get('has_3d_printing') == 'on'
            vendor.tube_laser_details = request.POST.get('tube_laser_details', '')
            vendor.sheet_laser_details = request.POST.get('sheet_laser_details', '')
            vendor.cnc_machining_details = request.POST.get('cnc_machining_details', '')
            vendor.vmc_machining_details = request.POST.get('vmc_machining_details', '')
            vendor.printing_3d_details = request.POST.get('printing_3d_details', '')
            vendor.max_material_thickness = request.POST.get('max_material_thickness', '')
            vendor.material_types = request.POST.get('material_types', '')
            vendor.production_capacity = request.POST.get('production_capacity', '')
            vendor.quality_certifications = request.POST.get('quality_certifications', '')
            
            vendor.save()
            
            messages.success(request, f'Vendor {vendor.company_name} updated successfully!')
            return redirect('crm_vendor_detail', vendor_id=vendor.id)
            
        except Exception as e:
            messages.error(request, f'Error updating vendor: {str(e)}')
    
    context = {
        'vendor': vendor,
        'vendor_status_choices': Vendor.VENDOR_STATUS,
        'vendor_service_choices': Vendor.VENDOR_TYPES,
    }
    
    return render(request, 'core/crm/vendor_edit.html', context)

@login_required
@require_http_methods(["POST"])
def crm_set_expected_date(request):
    """Set expected completion date for an order"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        order_id = request.POST.get('order_id')
        expected_date = request.POST.get('expected_completion_date')
        
        order = get_object_or_404(Order, order_id=order_id)
        order.expected_completion_date = expected_date
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Expected completion date set successfully',
            'expected_date': expected_date
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def crm_set_actual_date(request):
    """Set actual completion date for an order"""
    if not is_project_manager(request.user):
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    try:
        order_id = request.POST.get('order_id')
        actual_date = request.POST.get('actual_completion_date')
        
        order = get_object_or_404(Order, order_id=order_id)
        order.actual_completion_date = actual_date
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Actual completion date set successfully',
            'actual_date': actual_date
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
