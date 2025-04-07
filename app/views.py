from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import datetime, date, timedelta
import json
import razorpay
from decimal import Decimal
from .models import (Flat,FlatOccupant,Security,Visitor,Supermarket,ProductCategory,SupermarketProduct,MedicalStore,Medicine,Cart,Order,Payment,Service_Provider,Complaints,Notification,Facility,FacilityBooking,FacilityUsageLog,ChatRoom,Message)
# Create your views here.

# Index
def index(request):
    return render(request,'index.html')

# Logout
def logout(request):
    request.session.flush()
    return HttpResponse('''<script>alert('Logout Successfully');window.location.href="/";</script>''')





#################################################    ADMIN    ####################################################





# Admin login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            request.session['username'] = username
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/admin_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/admin_login/";</script>''')
    return render(request, 'admin_login.html')



# Admin Home
def admin_home(request):
    # Calculate statistics
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Flat and Occupancy stats
    total_flats = Flat.objects.count()
    occupied_flats = Flat.objects.filter(is_occupied=True).count()
    occupancy_rate = round((occupied_flats / total_flats) * 100) if total_flats > 0 else 0
    
    # Occupant stats
    total_occupants = FlatOccupant.objects.filter(is_active=True).count()
    new_occupants_this_month = FlatOccupant.objects.filter(
        move_in_date__month=today.month,
        move_in_date__year=today.year
    ).count()
    
    # Visitor stats
    total_visitors_today = Visitor.objects.filter(
        created_at__date=today
    ).count()
    pending_visitors = Visitor.objects.filter(status='Pending').count()
    
    # Service Provider stats
    total_service_providers = Service_Provider.objects.count()
    service_providers_by_type = Service_Provider.objects.values(
        'service_type'
    ).annotate(count=Count('id'))
    
    # Security stats
    total_security = Security.objects.count()
    security_by_shift = Security.objects.values(
        'shift_timing'
    ).annotate(count=Count('id'))
    
    # Complaint stats
    pending_complaints = Complaints.objects.filter(status='Pending').count()
    resolved_complaints = Complaints.objects.filter(status='Resolved').count()
    
    # Facility booking stats
    total_bookings = FacilityBooking.objects.count()
    active_bookings = FacilityBooking.objects.filter(
        Q(status='Approved') | Q(status='Pending')
    ).count()
    
    # Recent data for tables
    recent_visitors = Visitor.objects.order_by('-created_at')[:5]
    recent_complaints = Complaints.objects.order_by('-created_at')[:5]
    recent_bookings = FacilityBooking.objects.order_by('-created_at')[:5]
    recent_notifications = Notification.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Weekly visitor trends
    visitor_trends = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        count = Visitor.objects.filter(created_at__date=day).count()
        visitor_trends.append({
            'day': day.strftime('%a'),
            'count': count
        })
    
    context = {
        'total_flats': total_flats,
        'occupied_flats': occupied_flats,
        'occupancy_rate': occupancy_rate,
        'total_occupants': total_occupants,
        'new_occupants_this_month': new_occupants_this_month,
        'total_visitors_today': total_visitors_today,
        'pending_visitors': pending_visitors,
        'total_service_providers': total_service_providers,
        'service_providers_by_type': service_providers_by_type,
        'total_security': total_security,
        'security_by_shift': security_by_shift,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'recent_visitors': recent_visitors,
        'recent_complaints': recent_complaints,
        'recent_bookings': recent_bookings,
        'recent_notifications': recent_notifications,
        'visitor_trends': visitor_trends,
    }
    
    return render(request, 'admin_home.html', context)



# Admin add flat
def admin_add_flat(request):
    if request.method == "POST":
        flat_number = request.POST.get("flat_number").strip()
        floor = request.POST.get("floor")
        block = request.POST.get("block").strip()
        square_footage = request.POST.get("square_footage")
        bedrooms = request.POST.get("bedrooms") 
        if Flat.objects.filter(flat_number=flat_number).exists():
            return HttpResponse('''<script>alert('Flat number already exists!');window.location.href="/admin_add_flat";</script>''')
        try:
            flat = Flat(
                flat_number=flat_number,
                floor=int(floor),
                block=block if block else None,
                square_footage=int(square_footage) if square_footage else None,
                bedrooms=int(bedrooms)
            )
            flat.save()
            messages.success(request, 'Flat added successfully!')
            return redirect('admin_flat_list')
        except Exception as e:
            return HttpResponse(f'''<script>alert('Error: {str(e)}');window.location.href="/admin_add_flat";</script>''')
    return render(request, "admin_add_flat.html")



# Admin Flat list
def admin_flat_list(request):
    flats = Flat.objects.all().order_by('block', 'floor', 'flat_number')
    block_filter = request.GET.get('block')
    floor_filter = request.GET.get('floor')
    occupancy_filter = request.GET.get('occupancy')
    
    if block_filter:
        flats = flats.filter(block=block_filter)
    if floor_filter:
        flats = flats.filter(floor=floor_filter)
    if occupancy_filter:
        if occupancy_filter == 'occupied':
            flats = flats.filter(is_occupied=True)
        elif occupancy_filter == 'vacant':
            flats = flats.filter(is_occupied=False)
    
    total_flats = flats.count()
    vacant_flats_count = flats.filter(is_occupied=False).count()
    occupied_flats_count = flats.filter(is_occupied=True).count()
    
    blocks = Flat.objects.exclude(block__isnull=True).values_list('block', flat=True).distinct().order_by('block')
    floors = Flat.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    context = {
        'flats': flats,
        'blocks': blocks,
        'floors': floors,
        'current_block': block_filter,
        'current_floor': floor_filter,
        'current_occupancy': occupancy_filter,
        'total_flats': total_flats,
        'vacant_flats_count': vacant_flats_count,
        'occupied_flats_count': occupied_flats_count,
    }
    
    return render(request, 'admin_flat_list.html', context)



# Admin Edit Flat
def admin_edit_flat(request, flat_id):
    flat = get_object_or_404(Flat, id=flat_id)
    
    if request.method == 'POST':
        flat_number = request.POST.get('flat_number').strip()
        floor = request.POST.get('floor')
        block = request.POST.get('block').strip()
        square_footage = request.POST.get('square_footage')
        bedrooms = request.POST.get('bedrooms')
        
        if flat.flat_number != flat_number and Flat.objects.filter(flat_number=flat_number).exists():
            messages.error(request, 'Flat number already exists!')
            return redirect('admin_flat_list', flat_id=flat.id)
        
        try:
            flat.flat_number = flat_number
            flat.floor = int(floor)
            flat.block = block if block else None
            flat.square_footage = int(square_footage) if square_footage else None
            flat.bedrooms = int(bedrooms)
            flat.save()
            messages.success(request, 'Flat details updated successfully')
            return redirect('admin_flat_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_flat_list', flat_id=flat.id)
    
    return render(request, 'admin_flat_list.html', {'flat': flat})



# Admin delete Flat
def admin_delete_flat(request, flat_id):
    flat = get_object_or_404(Flat, id=flat_id)
    
    if request.method == 'POST':
        try:
            flat.delete()
            messages.success(request, 'Flat deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting flat: {str(e)}')
        return redirect('admin_flat_list')
    
    return render(request, 'admin_flat_list.html', {'flat': flat})



# Admin add security
def admin_add_security(request):
    if request.method == "POST":
        name = request.POST.get("name").strip()
        email = request.POST.get("email").strip()
        phone = request.POST.get("phone").strip()
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        address = request.POST.get("address").strip()
        shift_timing = request.POST.get("shift_timing")
        profile_image = request.FILES.get("profile_image")
        if Security.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert('Email already exists!');window.location.href="/admin_add_security";</script>''')
        if Security.objects.filter(username=username).exists():
            return HttpResponse('''<script>alert('Username already exists. Choose a unique username');window.location.href="/admin_add_security";</script>''')
        security = Security(
            name=name,
            email=email,
            phone=phone,
            age=age,
            gender=gender,
            username=username,
            password=password,
            address=address,
            shift_timing=shift_timing,
            profile_image=profile_image
        )
        security.save()
        subject = "Your Security Login Credentials"
        message = f"""
        Dear {name},

        You have been successfully added as a security staff member. Here are your login credentials:

        Username: {username}
        Password: {password}

        Please log in using these credentials and change your password after logging in.

        Regards,  
        Admin Team
        """
        send_mail(subject, message, "your_email@gmail.com", [email])
        return HttpResponse('''<script>alert('Security added successfully! Login details sent to email.');window.location.href="/admin_security_list";</script>''')
    return render(request, "admin_add_security.html")



# Admin Security list
def admin_security_list(request):
    securities = Security.objects.all().order_by('-created_at')
    return render(request,'admin_security_list.html',{'securities':securities})



# Admin Edit Security 
def admin_edit_security(request, security_id):
    security = get_object_or_404(Security, id=security_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        shift_timing = request.POST.get('shift_timing')
        security.name = name
        security.email = email
        security.phone = phone
        security.age = int(age)
        security.gender = gender
        security.username = username
        if password: 
            security.password = password 
        security.address = address
        security.shift_timing = shift_timing
        if 'profile_image' in request.FILES:
            security.profile_image = request.FILES['profile_image']
        security.save()
        messages.success(request, 'Security personnel details updated successfully')
        return redirect('admin_security_list')
    return render(request, 'admin_security_list.html', {'security': security})



# Admin delete Security 
def admin_delete_security(request, security_id):
    security = get_object_or_404(Security, id=security_id)
    if request.method == 'POST':
        security.delete()
        messages.success(request, 'Security personnel deleted successfully')
        return redirect('admin_security_list')
    return render(request, 'admin_security_list.html', {'security': security})



# Admin add flat occupant
def admin_add_flat_occupant(request):
    if request.method == "POST":
        flat_id = request.POST.get("flat")
        full_name = request.POST.get("full_name").strip()
        contact_number = request.POST.get("contact_number").strip()
        email = request.POST.get("email").strip()
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        occupant_type = request.POST.get("occupant_type")
        move_in_date = request.POST.get("move_in_date")
        move_out_date = request.POST.get("move_out_date")
        emergency_contact_name = request.POST.get("emergency_contact_name").strip()
        emergency_contact_number = request.POST.get("emergency_contact_number").strip()
        id_proof = request.FILES.get("id_proof")
        
        try:
            flat = Flat.objects.get(id=flat_id)
            flat.is_occupied=True
            flat.save()
        except Flat.DoesNotExist:
            return HttpResponse('''<script>alert('Flat does not exist!');window.location.href="/admin_add_flat_occupant";</script>''')
            
        if FlatOccupant.objects.filter(flat=flat).exists():
            return HttpResponse('''<script>alert('The flat number is already occupied!');window.location.href="/admin_add_flat_occupant";</script>''')

        if FlatOccupant.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert('Email already exists!');window.location.href="/admin_add_flat_occupant";</script>''')
        if FlatOccupant.objects.filter(username=username).exists():
            return HttpResponse('''<script>alert('Username already exists. Choose a unique username');window.location.href="/admin_add_flat_occupant";</script>''')
            
        occupant = FlatOccupant(
            flat=flat,
            full_name=full_name,
            contact_number=contact_number,
            email=email,
            username=username,
            password=password,
            date_of_birth=date_of_birth,
            gender=gender,
            occupant_type=occupant_type,
            move_in_date=move_in_date,
            move_out_date=move_out_date if move_out_date else None,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_number=emergency_contact_number,
            id_proof=id_proof
        )
        occupant.save()
        
        # Send email with credentials
        subject = "Your Flat Occupant Login Credentials"
        message = f"""
        Dear {full_name},

        You have been successfully registered as a {occupant_type} for flat {flat.flat_number}. 
        Here are your login credentials:

        Username: {username}
        Password: {password}

        Please log in using these credentials and change your password after logging in.

        Regards,  
        Admin Team
        """
        send_mail(subject, message, "your_email@gmail.com", [email])
        
        return HttpResponse('''<script>alert('Flat occupant added successfully! Login details sent to email.');window.location.href="/admin_flat_occupant_list";</script>''')
    
    flats = Flat.objects.all()
    return render(request, "admin_add_flat_occupant.html", {'flats': flats})



# Admin Flat occupant list
def admin_flat_occupant_list(request):
    occupants = FlatOccupant.objects.all().order_by('-created_at')
    flats = Flat.objects.all()  # Add this line
    return render(request, 'admin_flat_occupant_list.html', {
        'occupants': occupants,
        'flats': flats  # Add this line
    })



# Admin Edit Flat occupant 
def admin_edit_flat_occupant(request, occupant_id):
    occupant = get_object_or_404(FlatOccupant, id=occupant_id)
    if request.method == 'POST':
        flat_id = request.POST.get('flat')
        occupant.full_name = request.POST.get('full_name')
        occupant.contact_number = request.POST.get('contact_number')
        occupant.email = request.POST.get('email')
        occupant.username = request.POST.get('username')
        if request.POST.get('password'):
            occupant.password = request.POST.get('password')
        occupant.date_of_birth = request.POST.get('date_of_birth')
        occupant.gender = request.POST.get('gender')
        occupant.occupant_type = request.POST.get('occupant_type')
        occupant.move_in_date = request.POST.get('move_in_date')
        occupant.move_out_date = request.POST.get('move_out_date') or None
        occupant.emergency_contact_name = request.POST.get('emergency_contact_name')
        occupant.emergency_contact_number = request.POST.get('emergency_contact_number')
        
        try:
            flat = Flat.objects.get(id=flat_id)
            occupant.flat = flat
        except Flat.DoesNotExist:
            messages.error(request, 'Selected flat does not exist')
            return redirect('admin_edit_flat_occupant', occupant_id=occupant_id)
            
        if 'id_proof' in request.FILES:
            occupant.id_proof = request.FILES['id_proof']
            
        occupant.save()
        messages.success(request, 'Flat occupant details updated successfully')
        return redirect('admin_flat_occupant_list')
    
    flats = Flat.objects.all()
    return render(request, 'admin_flat_occupant_list.html', {'occupant': occupant, 'flats': flats})



# Admin delete Flat occupant 
def admin_delete_flat_occupant(request, occupant_id):
    occupant = get_object_or_404(FlatOccupant, id=occupant_id)
    if request.method == 'POST':
        occupant.delete()
        messages.success(request, 'Flat occupant deleted successfully')
        return redirect('admin_flat_occupant_list')
    return render(request, 'admin_flat_occupant_list.html', {'occupant': occupant})



# Admin add Service Provider
def admin_add_service_provider(request):
    if request.method == "POST":
        name = request.POST.get("name").strip()
        email = request.POST.get("email").strip()
        phone = request.POST.get("phone").strip()
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        address = request.POST.get("address").strip()
        service_type = request.POST.get("service_type")
        profile_image = request.FILES.get("profile_image")

        if Service_Provider.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert('Email already exists!');window.location.href="/admin_add_service_provider";</script>''')
        
        if Service_Provider.objects.filter(username=username).exists():
            return HttpResponse('''<script>alert('Username already exists. Choose a unique username');window.location.href="/admin_add_service_provider";</script>''')
        
        service_provider = Service_Provider(
            name=name,
            email=email,
            phone=phone,
            age=age,
            gender=gender,
            username=username,
            password=password,
            address=address,
            service_type=service_type,
            profile_image=profile_image
        )
        service_provider.save()

        subject = "Your Service Provider Login Credentials"
        message = f"""
        Dear {name},

        You have been successfully added as a service provider. Here are your login credentials:

        Username: {username}
        Password: {password}

        Please log in using these credentials and change your password after logging in.

        Regards,  
        Admin Team
        """
        send_mail(subject, message, "your_email@gmail.com", [email])

        return HttpResponse('''<script>alert('Service Provider added successfully! Login details sent to email.');window.location.href="/admin_service_provider_list";</script>''')
    
    return render(request, "admin_add_service_provider.html")



# Admin Service Provider List
def admin_service_provider_list(request):
    service_providers = Service_Provider.objects.all().order_by('-created_at')
    return render(request, 'admin_service_provider_list.html', {'service_providers': service_providers})



# Admin Edit Service Provider 
def admin_edit_service_provider(request, provider_id):
    service_provider = get_object_or_404(Service_Provider, id=provider_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        service_type = request.POST.get('service_type')

        service_provider.name = name
        service_provider.email = email
        service_provider.phone = phone
        service_provider.age = int(age)
        service_provider.gender = gender
        service_provider.username = username
        
        if password:  
            service_provider.password = password 
        
        service_provider.address = address
        service_provider.service_type = service_type

        if 'profile_image' in request.FILES:
            service_provider.profile_image = request.FILES['profile_image']

        service_provider.save()
        messages.success(request, 'Service provider details updated successfully')
        return redirect('admin_service_provider_list')

    return render(request, 'admin_service_provider_list.html', {'service_provider': service_provider})



# Admin Delete Service Provider 
def admin_delete_service_provider(request, provider_id):
    service_provider = get_object_or_404(Service_Provider, id=provider_id)

    if request.method == 'POST':
        service_provider.delete()
        messages.success(request, 'Service provider deleted successfully')
        return redirect('admin_service_provider_list')

    return render(request, 'admin_service_provider_list.html', {'service_provider': service_provider})



def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'admin_notifications.html', {'notifications': notifications})



def add_notification(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        is_active = request.POST.get('is_active') == 'on'
        
        Notification.objects.create(
            message=message,
            is_active=is_active
        )
        messages.success(request, 'Notification added successfully!')
        return redirect('notification_list')
    return render(request, 'admin_add_notification.html')




def edit_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    
    if request.method == 'POST':
        notification.message = request.POST.get('message')
        notification.is_active = request.POST.get('is_active') == 'on'
        notification.save()
        messages.success(request, 'Notification updated successfully!')
        return redirect('notification_list')
    
    return render(request, 'admin_edit_notification.html', {'notification': notification})




def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.delete()
    messages.success(request, 'Notification deleted successfully!')
    return redirect('notification_list')


def admin_visitor_list(request):
    today = date.today()
    visitors = Visitor.objects.all(
       
    ).order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    visitor_type_filter = request.GET.get('visitor_type')
    
    if status_filter:
        visitors = visitors.filter(status=status_filter)
    if visitor_type_filter:
        visitors = visitors.filter(visitor_type=visitor_type_filter)
    
    context = {
        'visitors': visitors,
        'status_choices': Visitor.STATUS_CHOICES,
        'visitor_type_choices': Visitor.VISITOR_TYPE_CHOICES,
        'today': today.strftime('%Y-%m-%d')
    }
    return render(request, 'admin_visitors_list.html', context)

def admin_visitor_detail(request, id):
    visitor = get_object_or_404(Visitor, id=id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in [choice[0] for choice in Visitor.STATUS_CHOICES]:
            visitor.status = new_status
            if new_status == 'CheckedIn':
                visitor.actual_arrival = timezone.now()
            elif new_status == 'CheckedOut':
                visitor.actual_departure = timezone.now()
            visitor.save()
            messages.success(request, f'Visitor status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status selected')
        
        return redirect('visitor_detail', id=visitor.id)
    
    context = {
        'visitor': visitor,
        'status_choices': Visitor.STATUS_CHOICES,
    }
    return render(request, 'admin_visitors_detail.html', context)


# For Admin
def all_complaints(request):
    complaints = Complaints.objects.all().order_by('-created_at')
    return render(request, 'all_complaints.html', {'complaints': complaints})

def complaint_detail(request, id):
    complaint = get_object_or_404(Complaints, id=id)
    
    if request.method == 'POST':
        complaint.reply = request.POST.get('reply')
        complaint.status = request.POST.get('status')
        complaint.is_read_by_admin = True
        complaint.save()
        messages.success(request, "Response submitted successfully!")
        return redirect('all_complaints')
    
    return render(request, 'complaint_detail.html', {'complaint': complaint})




#################################################    FLAT OCCUPANT    ####################################################





# Flat occupant login
def flat_occupant_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if FlatOccupant.objects.filter(username=username, password=password).exists():
            flatoccupant = FlatOccupant.objects.get(username=username)
            request.session['email'] = flatoccupant.email
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/flat_occupant_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/flat_occupant_login/";</script>''')
    return render(request,'flat_occupant_login.html')



# Flat Occupant Home
def flat_occupant_home(request):
    semail = request.session.get('email')
    try:
        occupant = FlatOccupant.objects.get(email=semail)
    except FlatOccupant.DoesNotExist:
        return render(request, 'error.html', {'message': 'User not found'})
    pending_orders = Order.objects.filter(user=occupant, status='Pending').count()
    today_visitors = Visitor.objects.filter(flat=occupant.flat,expected_arrival__date=timezone.now().date()).count()
    open_complaints = Complaints.objects.filter(flat_occupant=occupant, status='Pending').count()
    cart_items = Cart.objects.filter(user=occupant).count()
    unread_notifications = Notification.objects.filter(is_active=True).count()
    last_login = timezone.now()
    context = {
        'occupant': occupant,
        'pending_orders': pending_orders,
        'today_visitors': today_visitors,
        'open_complaints': open_complaints,
        'cart_items': cart_items,
        'unread_notifications': unread_notifications,
        'last_login': last_login,
    }
    return render(request, 'flat_occupant_home.html', context)



# Flat Occupant Profile
def flat_occupant_profile(request):
    semail=request.session.get('email')
    flat_occupant=FlatOccupant.objects.get(email=semail)
    return render(request,'flat_occupant_profile.html',{'flat_occupant':flat_occupant})



# Flat Occupant view supermarket list
def flat_occupant_supermarket_list(request):
    query = request.GET.get('query', '')
    is_delivery = request.GET.get('delivery', '')
    is_open_sunday = request.GET.get('sunday', '')
    
    supermarkets = Supermarket.objects.filter(is_active=True)
    
    if query:
        supermarkets = supermarkets.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        )
    
    if is_delivery:
        supermarkets = supermarkets.filter(delivery_available=True)
        
    if is_open_sunday:
        supermarkets = supermarkets.filter(sunday_available=True)
    
    context = {
        'supermarkets': supermarkets,
        'query': query,
        'is_delivery': is_delivery,
        'is_open_sunday': is_open_sunday,
    }
    
    return render(request, 'flat_occupant_supermarket_list.html', context)



# Flat occupant view supermarket products
def flat_occupant_supermarket_products(request, supermarket_id):
    supermarket = get_object_or_404(Supermarket, id=supermarket_id, is_active=True)
    categories = ProductCategory.objects.filter(supermarket=supermarket)
    
    category_id = request.GET.get('category', '')
    query = request.GET.get('query', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = SupermarketProduct.objects.filter(supermarket=supermarket, is_available=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))
    
    context = {
        'supermarket': supermarket,
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'flat_occupant_supermarket_products.html', context)



# Flat occupant view supermarket products details
def flat_occupant_products(request, product_id):
    product = get_object_or_404(SupermarketProduct, id=product_id, is_available=True)
    supermarket = product.supermarket
    
    related_products = SupermarketProduct.objects.filter(
        category=product.category,
        supermarket=supermarket,
        is_available=True
    ).exclude(id=product_id)[:4]  
    context = {
        'product': product,
        'supermarket': supermarket,
        'related_products': related_products,
    }
    
    return render(request, 'flat_occupant_products.html', context)



# Flat occupant view products list
def flat_occupant_product_list(request):
    product = SupermarketProduct.objects.all()
    context = {
        'product': product,
    }
    return render(request, 'flat_occupant_product_list.html', context)



# Flat occupant view medicalstore list
def flat_occupant_medicalstore_list(request):
    query = request.GET.get('query', '')
    is_delivery = request.GET.get('delivery', '')
    is_open_sunday = request.GET.get('sunday', '')
    
    medical_stores = MedicalStore.objects.filter(is_active=True)
    
    if query:
        medical_stores = medical_stores.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(owner_name__icontains=query)
        )
    
    if is_delivery:
        medical_stores = medical_stores.filter(delivery_available=True)
        
    if is_open_sunday:
        medical_stores = medical_stores.filter(sunday_available=True)
    
    context = {
        'medical_stores': medical_stores,
        'query': query,
        'is_delivery': is_delivery,
        'is_open_sunday': is_open_sunday,
    }
    
    return render(request, 'flat_occupant_medicalstore_list.html', context)



# Flat occupant view medical store products list
def flat_occupant_medicalstore_medicines(request, medicalstore_id):
    medical_store = get_object_or_404(MedicalStore, id=medicalstore_id, is_active=True)
    
    query = request.GET.get('query', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    manufacturer_filter = request.GET.get('manufacturer', '')
    
    medicines = Medicine.objects.filter(medicalstore=medical_store, is_available=True)
    
    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(manufacturer__icontains=query)
        )
    
    if min_price:
        medicines = medicines.filter(price__gte=float(min_price))
    if max_price:
        medicines = medicines.filter(price__lte=float(max_price))
    
    if manufacturer_filter:
        medicines = medicines.filter(manufacturer__iexact=manufacturer_filter)
    
    # Get unique manufacturers for filter dropdown
    manufacturers = Medicine.objects.filter(
        medicalstore=medical_store
    ).order_by('manufacturer').values_list('manufacturer', flat=True).distinct()
    
    context = {
        'medical_store': medical_store,
        'medicines': medicines,
        'manufacturers': manufacturers,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'selected_manufacturer': manufacturer_filter,
    }
    
    return render(request, 'flat_occupant_medicalstore_medicines.html', context)



# Flat occupant view medical store products details
def flat_occupant_medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id, is_available=True)
    medical_store = medicine.medicalstore
    
    # Get related medicines (same manufacturer or same medical store)
    related_medicines = Medicine.objects.filter(
        Q(medicalstore=medical_store) | 
        Q(manufacturer=medicine.manufacturer),
        is_available=True
    ).exclude(id=medicine_id).distinct()[:4]
    
    context = {
        'medicine': medicine,
        'medical_store': medical_store,
        'related_medicines': related_medicines,
    }
    
    return render(request, 'flat_occupant_medicine_detail.html', context)



# Flat occupant view medicine list
def flat_occupant_medicine_list(request):
    product = Medicine.objects.all()
    context = {
        'product': product,
    }
    return render(request, 'flat_occupant_medicine_list.html', context)


# Flat occupant add to cart 
def flat_occupant_add_to_cart(request, item_type, item_id):
    semail = request.session.get('email')
    user = get_object_or_404(FlatOccupant, email=semail)
    
    # Get the item regardless of request method
    if item_type == 'product':
        item = get_object_or_404(SupermarketProduct, id=item_id)
        redirect_name = 'product_detail'
        field_name = 'product'  # Field name in Cart model
    else:  # medicine
        item = get_object_or_404(Medicine, id=item_id)
        redirect_name = 'medicine_detail'
        field_name = 'medicines'  # Field name in Cart model
    
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        
        # Check stock availability
        if quantity > item.stock or quantity <= 0:
            messages.error(request, f"Stock Alert! Enter a valid quantity. Available stock: {item.stock}")
            return redirect(redirect_name, item_id=item_id)
        
        total_price = quantity * item.price
        
        # Create or update cart item using the correct field name
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            **{field_name: item},  # Use the correct field name here
            defaults={
                "quantity": quantity,
                "price": total_price,
            }
        )
        
        if not created:
            # Update existing cart item
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * item.price
            cart_item.save()

        messages.success(request, "Item added to cart successfully!")
        return redirect("flat_occupant_cart_view")

    return render(request, "add_to_cart.html", {
        "item": item,
        "item_type": item_type,
        "redirect_name": redirect_name
    })



# Flat occupant view cart
def flat_occupant_cart_view(request):
    """
    Displays the unified cart containing both products and medicines
    """
    semail = request.session.get('email')
    user = get_object_or_404(FlatOccupant, email=semail)
    cart_items = Cart.objects.filter(user=user)
    
    # Process cart items with their details
    processed_items = []
    for item in cart_items:
        if item.product:
            item_type = 'product'
            item_obj = item.product
        else:
            item_type = 'medicine'
            item_obj = item.medicines
            
        processed_items.append({
            'id': item.id,
            'item': item_obj,
            'item_type': item_type,
            'quantity': item.quantity,
            'price': item_obj.price,
            'total_price': item.quantity * item_obj.price,
        })
    
    total_price = sum(item['total_price'] for item in processed_items)
    
    return render(request, "cart.html", {
        "cart_items": processed_items,
        "total_price": total_price,
    })



# Flat occupant remove cart
def flat_occupant_remove_from_cart(request):
    """
    Handles removing items from cart via AJAX
    """
    if request.method == "POST":
        semail = request.session.get('email')
        user = get_object_or_404(FlatOccupant, email=semail)
        item_id = request.POST.get("item_id")
        cart_item = get_object_or_404(Cart, id=item_id, user=user)
        cart_item.delete()
        
        # Recalculate total
        cart_items = Cart.objects.filter(user=user)
        total_price = sum(
            (item.product.price if item.product else item.medicines.price) * item.quantity 
            for item in cart_items
        )
        
        return JsonResponse({"success": True, "total_price": total_price})
    return JsonResponse({"success": False})



# Flat occupant update cart
def flat_occupant_update_cart(request):
    """
    Handles updating cart quantities via AJAX
    """
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity")
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        cart_item = get_object_or_404(Cart, id=item_id)
        
        # Check stock based on item type
        if cart_item.product:
            if quantity > cart_item.product.stock:
                return JsonResponse({"error": "Not enough stock available."}, status=400)
            item_price = cart_item.product.price
        else:
            if quantity > cart_item.medicines.stock:
                return JsonResponse({"error": "Not enough stock available."}, status=400)
            item_price = cart_item.medicines.price
        
        # Update cart item
        cart_item.quantity = quantity
        cart_item.price = quantity * item_price
        cart_item.save()
        
        # Recalculate total
        cart_items = Cart.objects.filter(user=cart_item.user)
        total_price = sum(
            (item.product.price if item.product else item.medicines.price) * item.quantity 
            for item in cart_items
        )
        
        return JsonResponse({
            "success": True,
            "item_total_price": quantity * item_price,
            "total_price": total_price
        })



# Flat occupant place order
def flat_occupant_place_order(request):
    """
    Creates orders from cart items for both products and medicines
    """
    semail = request.session.get('email')
    user = get_object_or_404(FlatOccupant, email=semail)
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('flat_occupant_cart_view')
    
    for item in cart_items:
        # Determine if it's a product or medicine
        if item.product:
            order = Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity,
                status="Pending",
            )
            # Reduce product stock
            item.product.stock -= item.quantity
            item.product.save()
            
            # Send email to supermarket
            send_mail(
                subject="New Order Received",
                message=f"A new order for {item.product.name} has been placed by {user.full_name}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[item.product.supermarket.provider.email],
            )
        else:  # medicine
            order = Order.objects.create(
                user=user,
                medicines=item.medicines,
                quantity=item.quantity,
                price=item.medicines.price * item.quantity,
                status="Pending",
            )
            # Reduce medicine stock
            item.medicines.stock -= item.quantity
            item.medicines.save()
            
            # Send email to medical store
            send_mail(
                subject="New Medicine Order Received",
                message=f"A new order for {item.medicines.name} has been placed by {user.full_name}.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[item.medicines.medicalstore.provider.email],
            )
    
    # Clear cart after creating orders
    cart_items.delete()
    
    messages.success(request, "Orders placed successfully!")
    return redirect('flat_occupant_orders')



# Flat occupant view placed order
def flat_occupant_orders(request):
    """
    Displays all orders (both products and medicines) for the user
    """
    semail = request.session.get('email')
    user = get_object_or_404(FlatOccupant, email=semail)
    orders = Order.objects.filter(user=user).order_by('-placed_at')
    
    # Calculate total for payable orders
    payable_orders = orders.filter(status='Accepted', payment_status='Pending')
    total_payable_amount = sum(order.price for order in payable_orders)
    
    context = {
        'orders': orders,
        'payable_orders': payable_orders,
        'total_payable_amount': total_payable_amount,
        'user': user,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'orders.html', context)



# Flat occupant order payment

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
@csrf_exempt
def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = int(float(data['amount']) * 100)  # Convert to paise
            order_ids = data['order_ids']
            
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'receipt': f"orders_{'_'.join(order_ids)}",
                'payment_capture': 1
            })
            
            return JsonResponse({
                'key': settings.RAZORPAY_KEY_ID,
                'amount': amount,
                'razorpay_order_id': razorpay_order['id'],
                'currency': 'INR'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def verify_razorpay_payment(request):
    semail = request.session.get('email')
    user = get_object_or_404(FlatOccupant, email=semail)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_ids = data['order_ids']
            
            # Verify payment signature
            params = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            client.utility.verify_payment_signature(params)
            
            # Update all orders
            orders = Order.objects.filter(id__in=order_ids, user=user)
            for order in orders:
                order.payment_status = 'Completed'
                order.save()
                
                # Create payment record
                Payment.objects.create(
                    order=order,
                    user=user,
                    amount=order.price * order.quantity,
                    payment_status='Completed',
                    transaction_id=data['razorpay_payment_id'],
                )
            
            return JsonResponse({'success': True})
        except razorpay.errors.SignatureVerificationError as e:
            return JsonResponse({'success': False, 'message': 'Invalid payment signature'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'error': 'Invalid request'}, status=400)



#  Flat Occupant visitor management dashboard
def resident_dashboard(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        occupant = FlatOccupant.objects.get(email=request.session['email'])
    except FlatOccupant.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    visitors = Visitor.objects.filter(requested_by=occupant).order_by('-created_at')
    return render(request, 'resident_dashboard.html', {
        'occupant': occupant,
        'visitors': visitors
    })



#  Flat Occupant add visitors
def add_expected_visitor(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        occupant = FlatOccupant.objects.get(email=request.session['email'])
    except FlatOccupant.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        purpose = request.POST.get('purpose')
        vehicle_number = request.POST.get('vehicle_number')
        expected_arrival = request.POST.get('expected_arrival')
        
        if not name or not phone:
            messages.error(request, "Name and phone are required fields")
            return render(request, 'add_expected_visitor.html', {
                'occupant': occupant,
                'name': name,
                'phone': phone,
                'purpose': purpose,
                'vehicle_number': vehicle_number,
                'expected_arrival': expected_arrival
            })
        
        visitor = Visitor(
            name=name,
            phone=phone,
            purpose=purpose,
            vehicle_number=vehicle_number,
            expected_arrival=expected_arrival,
            requested_by=occupant,
            flat=occupant.flat,
            visitor_type='Expected',
            status='Approved'
        )
        visitor.save()
        
        messages.success(request, f"Visitor added successfully! Verification code: {visitor.verification_code}")
        return redirect('resident_dashboard')
    
    return render(request, 'add_expected_visitor.html', {'occupant': occupant})


#  Flat Occupant visitors history
def resident_visitor_history(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        occupant = FlatOccupant.objects.get(email=request.session['email'])
    except FlatOccupant.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    # Get all visitors for this resident, ordered by most recent
    visitors = Visitor.objects.filter(requested_by=occupant).order_by('-created_at')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        visitors = visitors.filter(created_at__date=date_filter)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        visitors = visitors.filter(status=status_filter)
    
    return render(request, 'resident_visitor_history.html', {
        'occupant': occupant,
        'visitors': visitors,
        'date_filter': date_filter or '',
        'status_filter': status_filter or ''
    })



# Helper function to get flat occupant from session
def get_flat_occupant(request):
    if 'email' in request.session:
        try:
            return FlatOccupant.objects.get(email=request.session['email'])
        except FlatOccupant.DoesNotExist:
            return None
    return None



#  Flat Occupant facility list
def facility_list(request):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facilities = Facility.objects.filter(is_active=True)
    
    # Filter by facility type if specified
    facility_type = request.GET.get('type')
    if facility_type:
        facilities = facilities.filter(facility_type=facility_type)
    
    context = {
        'facilities': facilities,
        'facility_types': Facility.FACILITY_TYPES,
    }
    return render(request, 'facility_list.html', context)



#  Flat Occupant facility details
def facility_detail(request, facility_id):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facility = get_object_or_404(Facility, id=facility_id, is_active=True)
    
    # Check if the user has any upcoming bookings for this facility
    user_bookings = FacilityBooking.objects.filter(
        user=flat_occupant,
        facility=facility,
        booking_date__gte=date.today(),
        status__in=['Pending', 'Approved']
    ).exists()
    
    context = {
        'facility': facility,
        'has_upcoming_booking': user_bookings,
    }
    return render(request, 'facility_detail.html', context)



#  Flat Occupant book facility
def book_facility(request, facility_id):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facility = get_object_or_404(Facility, id=facility_id, is_active=True)
    
    if request.method == 'POST':
        try:
            booking_date = request.POST.get('booking_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            purpose = request.POST.get('purpose', '')
            
            # Convert strings to proper date/time objects
            booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()
            
            # Validate booking time is within facility operating hours
            if start_time < facility.opening_time or end_time > facility.closing_time:
                messages.error(request, 'Booking time must be within facility operating hours.')
                return redirect('book_facility', facility_id=facility_id)
            
            # Check for overlapping bookings
            overlapping_bookings = FacilityBooking.objects.filter(
                facility=facility,
                booking_date=booking_date,
                status__in=['Approved', 'Pending'],
            ).filter(
                Q(start_time__lt=end_time, end_time__gt=start_time)
            )
            
            if overlapping_bookings.exists():
                messages.error(request, 'The selected time slot is already booked. Please choose another time.')
                return redirect('book_facility', facility_id=facility_id)
            
            # Create the booking
            booking = FacilityBooking(
                facility=facility,
                user=flat_occupant,
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose,
                status='Pending'
            )
            booking.save()
            
            messages.success(request, 'Your booking request has been submitted for approval.')
            return redirect('my_bookings')
        
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
    
    # Default to today's date for the booking form
    default_date = date.today().strftime('%Y-%m-%d')
    default_start = facility.opening_time.strftime('%H:%M')
    default_end = (datetime.combine(date.today(), facility.opening_time) + timedelta(hours=1)).time().strftime('%H:%M')
    
    context = {
        'facility': facility,
        'default_date': default_date,
        'default_start': default_start,
        'default_end': default_end,
    }
    return render(request, 'book_facility.html', context)



#  Flat Occupant facility bookings
def my_bookings(request):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    bookings = FacilityBooking.objects.filter(user=flat_occupant).order_by('-booking_date', '-start_time')
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_choices': FacilityBooking.STATUS_CHOICES,
    }
    return render(request, 'my_bookings.html', context)



#  Flat Occupant cancel facility bookings
def cancel_booking(request, booking_id):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    booking = get_object_or_404(FacilityBooking, id=booking_id, user=flat_occupant)
    
    if request.method == 'POST':
        if booking.status in ['Pending', 'Approved']:
            booking.status = 'Cancelled'
            booking.save()
            messages.success(request, 'Booking has been cancelled.')
        else:
            messages.error(request, 'Cannot cancel a booking that is already completed or cancelled.')
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'cancel_booking.html', context)



#  Flat Occupant check in facility
def check_in(request, booking_id):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    booking = get_object_or_404(
        FacilityBooking, 
        id=booking_id, 
        user=flat_occupant,
        status='Approved'
    )
    
    # if booking.booking_date != date.today():
    #     messages.error(request, 'You can only check in on the day of your booking.')
    #     return redirect('my_bookings')
    
    if booking.checked_in:
        messages.warning(request, 'You have already checked in for this booking.')
        return redirect('my_bookings')
    
    # Check if current time is within 30 minutes of booking start time
    current_time = datetime.now().time()
    booking_start = booking.start_time
    time_diff = (datetime.combine(date.today(), current_time) - datetime.combine(date.today(), booking_start))
    
    # if abs(time_diff.total_seconds()) > 1800:  # 30 minutes in seconds
    #     messages.error(request, 'You can only check in within 30 minutes of your booking start time.')
    #     return redirect('my_bookings')
    
    # Perform check-in
    booking.checked_in = True
    booking.checked_in_time = datetime.now()
    booking.save()
    
    # Create usage log
    usage_log = FacilityUsageLog(
        booking=booking,
        actual_start_time=datetime.now(),
        notes=f"Checked in by {flat_occupant.full_name}"
    )
    usage_log.save()
    
    messages.success(request, 'Successfully checked in! Enjoy your time at the facility.')
    return redirect('my_bookings')



#  Flat Occupant check out facility
from django.utils import timezone  
def check_out(request, booking_id):
    flat_occupant = get_flat_occupant(request)
    if not flat_occupant:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    booking = get_object_or_404(
        FacilityBooking, 
        id=booking_id, 
        user=flat_occupant,
        status='Approved',
        checked_in=True
    )
    booking.status='Completed'
    if not booking.checked_in:
        messages.error(request, 'You must check in before you can check out.')
        return redirect('my_bookings')
    
    if booking.checked_out_time:
        messages.warning(request, 'You have already checked out from this booking.')
        return redirect('my_bookings')
    
    # Perform check-out with timezone-aware datetime
    booking.checked_out_time = timezone.now()
    booking.save()
    
    # Update usage log
    try:
        usage_log = FacilityUsageLog.objects.get(booking=booking)
        usage_log.actual_end_time = timezone.now()
        
        # Calculate duration in minutes
        if usage_log.actual_start_time:
            # Ensure both datetimes are timezone-aware before subtraction
            if timezone.is_aware(usage_log.actual_start_time) and timezone.is_aware(usage_log.actual_end_time):
                duration = usage_log.actual_end_time - usage_log.actual_start_time
                usage_log.duration_minutes = duration.total_seconds() // 60
            else:
                # Handle case where times might not be timezone-aware
                usage_log.duration_minutes = 0  # or some default value
        
        usage_log.notes = f"Checked out by {flat_occupant.full_name}"
        usage_log.save()
    except FacilityUsageLog.DoesNotExist:
        pass
    
    messages.success(request, 'Successfully checked out! Thank you for using our facility.')
    return redirect('my_bookings')



# Common function to get user type
def get_user_type(request):
    if 'email' in request.session:
        try:
            if FlatOccupant.objects.filter(email=request.session['email']).exists():
                return 'flat_occupant'
            elif Service_Provider.objects.filter(email=request.session['email']).exists():
                return 'service_provider'
        except:
            return None
    return None



# For Flat Occupants
def submit_complaint(request):
    user_type = get_user_type(request)
    if user_type != 'flat_occupant':
        messages.error(request, "You need to login as a flat occupant to submit complaints")
        return redirect('login')
    
    flat_occupant = FlatOccupant.objects.get(email=request.session['email'])
    
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint')
        Complaints.objects.create(
            flat_occupant=flat_occupant,
            complaint=complaint_text,
            status='Pending'
        )
        messages.success(request, "Complaint submitted successfully!")
        return redirect('view_my_complaints')
    
    return render(request, 'submit_complaint.html')

def view_my_complaints(request):
    user_type = get_user_type(request)
    if user_type != 'flat_occupant':
        messages.error(request, "Access denied")
        return redirect('login')
    
    flat_occupant = FlatOccupant.objects.get(email=request.session['email'])
    complaints = Complaints.objects.filter(flat_occupant=flat_occupant).order_by('-created_at')
    
    return render(request, 'my_complaints.html', {'complaints': complaints})





#################################################    SECURITY    ####################################################





# Security login
def security_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Security.objects.filter(username=username, password=password).exists():
            security = Security.objects.get(username=username)
            request.session['email'] = security.email
            request.session['security_id'] = security.id
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/security_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/security_login/";</script>''')
    return render(request,'security_login.html')



# Security Home
def security_home(request):
    security_id = request.session.get('security_id', 1)  
    try:
        security = Security.objects.get(id=security_id)
    except Security.DoesNotExist:
        security = Security.objects.first()
    
    # Today's date range
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Get statistics
    active_chats_count = ChatRoom.objects.filter(security=security).count()
    
    pending_visitors_count = Visitor.objects.filter(
        status='Pending', 
        expected_arrival__gte=today_start
    ).count()
    
    todays_checkins_count = Visitor.objects.filter(
        status='CheckedIn',
        actual_arrival__range=(today_start, today_end)
    ).count()
    
    total_occupants_count = FlatOccupant.objects.filter(is_active=True).count()
    
    # Get recent chats with unread messages
    recent_chats = ChatRoom.objects.filter(security=security).order_by('-last_message_time')[:5]
    
    # Check for unread messages in each chat room
    for chat in recent_chats:
        chat.has_unread = Message.objects.filter(
            chat_room=chat,
            sender_type='Occupant',
            is_read=False
        ).exists()
    
    # Get pending visitors for today and future
    pending_visitors = Visitor.objects.filter(
        status='Pending',
        expected_arrival__gte=today_start
    ).order_by('expected_arrival')[:5]
    
    # Get checked-in visitors today
    checked_in_visitors = Visitor.objects.filter(
        status='CheckedIn',
        actual_arrival__range=(today_start, today_end)
    ).order_by('-actual_arrival')[:5]
    
    context = {
        'security': security,
        'active_chats_count': active_chats_count,
        'pending_visitors_count': pending_visitors_count,
        'todays_checkins_count': todays_checkins_count,
        'total_occupants_count': total_occupants_count,
        'recent_chats': recent_chats,
        'pending_visitors': pending_visitors,
        'checked_in_visitors': checked_in_visitors,
    }
    
    return render(request, 'security_home.html', context)



# Security visitor management dashboard
def security_dashboard(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        security = Security.objects.get(email=request.session['email'])
    except Security.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    active_visitors = Visitor.objects.filter(status='CheckedIn')
    pending_visitors = Visitor.objects.filter(status='Approved', actual_arrival__isnull=True)
    return render(request, 'security_dashboard.html', {
        'security': security,
        'active_visitors': active_visitors,
        'pending_visitors': pending_visitors
    })



# Security handle visitors
def handle_unexpected_visitor(request):
    if 'email' not in request.session:
        return redirect('login')
    try:
        security = Security.objects.get(email=request.session['email'])
    except Security.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        purpose = request.POST.get('purpose')
        vehicle_number = request.POST.get('vehicle_number')
        id_proof_type = request.POST.get('id_proof_type')
        id_proof_number = request.POST.get('id_proof_number')
        flat_id = request.POST.get('flat')  # Optional field
        occupant_id = request.POST.get('occupant')  # Optional field
        
        if not name or not phone:
            messages.error(request, "Name and phone are required fields")
            return render(request, 'handle_unexpected_visitor.html', {
                'security': security,
                'name': name,
                'phone': phone,
                'purpose': purpose,
                'vehicle_number': vehicle_number,
                'id_proof_type': id_proof_type,
                'id_proof_number': id_proof_number,
                'flats': Flat.objects.all(),  # Add this for the template
                'occupants': FlatOccupant.objects.all()  # Add this for the template
            })
        
        visitor = Visitor(
            name=name,
            phone=phone,
            purpose=purpose,
            vehicle_number=vehicle_number,
            id_proof_type=id_proof_type,
            id_proof_number=id_proof_number,
            visitor_type='Unexpected',
            is_unexpected=True,
            status='CheckedIn',
            checked_in_by=security,
            actual_arrival=timezone.now()
        )
        
        # Add optional flat and occupant if provided
        if flat_id:
            try:
                visitor.flat = Flat.objects.get(id=flat_id)
            except Flat.DoesNotExist:
                pass
        
        if occupant_id:
            try:
                visitor.requested_by = FlatOccupant.objects.get(id=occupant_id)
            except FlatOccupant.DoesNotExist:
                pass
        
        if 'id_proof_image' in request.FILES:
            id_proof_image = request.FILES['id_proof_image']
            fs = FileSystemStorage()
            filename = fs.save(f'visitor_ids/{id_proof_image.name}', id_proof_image)
            visitor.id_proof_image = filename
        
        visitor.save()
        messages.success(request, "Unexpected visitor checked in successfully!")
        return redirect('security_dashboard')
    
    # For GET request, pass flats and occupants to the template
    return render(request, 'handle_unexpected_visitor.html', {
        'security': security,
        'flats': Flat.objects.all(),
        'occupants': FlatOccupant.objects.all()
    })



# Security visitor checkin handling
def check_in_visitor(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        security = Security.objects.get(email=request.session['email'])
    except Security.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        id_proof_type = request.POST.get('id_proof_type')
        id_proof_number = request.POST.get('id_proof_number')
        
        try:
            visitor = Visitor.objects.get(verification_code=verification_code, status='Approved')
            visitor.status = 'CheckedIn'
            visitor.checked_in_by = security
            visitor.actual_arrival = timezone.now()
            visitor.id_proof_type = id_proof_type
            visitor.id_proof_number = id_proof_number
            
            if 'id_proof_image' in request.FILES:
                id_proof_image = request.FILES['id_proof_image']
                fs = FileSystemStorage()
                filename = fs.save(f'visitor_ids/{id_proof_image.name}', id_proof_image)
                visitor.id_proof_image = filename
            
            visitor.save()
            messages.success(request, "Visitor checked in successfully!")
            return redirect('security_dashboard')
        except Visitor.DoesNotExist:
            messages.error(request, "Invalid verification code or visitor not approved")
    
    return render(request, 'check_in_visitor.html', {'security': security})



# Security visitor checkout handling
def check_out_visitor(request, visitor_id):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        security = Security.objects.get(email=request.session['email'])
    except Security.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    if request.method == 'POST':
        visitor.status = 'CheckedOut'
        visitor.checked_out_by = security
        visitor.actual_departure = timezone.now()
        visitor.save()
        messages.success(request, "Visitor checked out successfully!")
        return redirect('security_dashboard')
    
    return render(request, 'check_out_visitor.html', {
        'security': security,
        'visitor': visitor
    })



# Security visitors history
def security_visitor_history(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        security = Security.objects.get(email=request.session['email'])
    except Security.DoesNotExist:
        messages.error(request, "Invalid user session")
        return redirect('login')
    
    # Get all visitors (security can see all)
    visitors = Visitor.objects.all().order_by('-created_at')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        visitors = visitors.filter(created_at__date=date_filter)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        visitors = visitors.filter(status=status_filter)
    
    # Filter by flat if provided
    flat_filter = request.GET.get('flat')
    if flat_filter:
        visitors = visitors.filter(flat__flat_number=flat_filter)
    
    return render(request, 'security_visitor_history.html', {
        'security': security,
        'visitors': visitors,
        'date_filter': date_filter or '',
        'status_filter': status_filter or '',
        'flat_filter': flat_filter or '',
        'all_flats': Flat.objects.all()  # For dropdown
    })




#################################################    SERVICE PROVIDER    ####################################################



# Service provider login
def service_provider_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Service_Provider.objects.filter(username=username, password=password).exists():
            provider = Service_Provider.objects.get(username=username)
            request.session['email'] = provider.email
            request.session['provider_id'] = provider.id
            request.session['service_type'] = provider.service_type
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/service_provider_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/service_provider_login/";</script>''')
    return render(request, 'service_provider_login.html')



# Service provider home
def service_provider_home(request):
    if 'email' not in request.session:
        return redirect('/service_provider_login/')
    
    try:
        provider = Service_Provider.objects.get(id=request.session['provider_id'])
        service_type = request.session['service_type']
        
        context = {
            'provider': provider,
            'service_type': service_type,
            'active_tab': 'dashboard'
        }
        
        if service_type == 'Gym':
            context['title'] = "Gym Management Dashboard"
            facility = Facility.objects.filter(facility_type='Gym').first()
            bookings = FacilityBooking.objects.filter(facility=facility)
            
            context['metrics'] = {
                'members': FlatOccupant.objects.count(),
                'bookings': bookings.count(),
                'active_bookings': bookings.filter(status='Approved').count(),
            }
            context['recent_activities'] = FacilityBooking.objects.filter(
                facility__facility_type='Gym'
            ).order_by('-created_at')[:5]
            
        elif service_type == 'Swimming Pool':
            context['title'] = "Swimming Pool Management Dashboard"
            facility = Facility.objects.filter(facility_type='Swimming Pool').first()
            bookings = FacilityBooking.objects.filter(facility=facility)
            
            context['metrics'] = {
                'bookings': bookings.count(),
                'active_bookings': bookings.filter(status='Approved').count(),
                'today_bookings': bookings.filter(booking_date=timezone.now().date()).count(),
            }
            context['recent_activities'] = FacilityBooking.objects.filter(
                facility__facility_type='Swimming Pool'
            ).order_by('-created_at')[:5]
            
        elif service_type == 'Medical Store':
            context['title'] = "Medical Store Management Dashboard"
            medical_store = MedicalStore.objects.filter(provider=provider).first()
            medicines = Medicine.objects.filter(medicalstore=medical_store) if medical_store else []
            orders = Order.objects.filter(medicines__in=medicines) if medical_store else []
            
            context['metrics'] = {
                'inventory': medicines.count(),
                'orders': orders.count(),
                'pending_orders': orders.filter(status='Pending').count(),
            }
            context['recent_activities'] = Order.objects.filter(
                medicines__medicalstore__provider=provider
            ).distinct().order_by('-placed_at')[:5]
            
        elif service_type == 'Supermarket':
            context['title'] = "Supermarket Management Dashboard"
            supermarket = Supermarket.objects.filter(provider=provider).first()
            products = SupermarketProduct.objects.filter(supermarket=supermarket) if supermarket else []
            orders = Order.objects.filter(product__in=products) if supermarket else []
            
            context['metrics'] = {
                'products': products.count(),
                'orders': orders.count(),
                'pending_orders': orders.filter(status='Pending').count(),
            }
            context['recent_activities'] = Order.objects.filter(
                product__supermarket__provider=provider
            ).distinct().order_by('-placed_at')[:5]
        
        return render(request, 'service_provider_home.html', context)
    
    except Service_Provider.DoesNotExist:
        return HttpResponse('''<script>alert('Session expired');window.location.href="/service_provider_login/";</script>''')



# Service Provider add Supermarket
def service_provider_add_supermarket(request):
    if request.method == "POST":
        name = request.POST.get("name").strip()
        location = request.POST.get("location").strip()
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        delivery_available = request.POST.get("delivery_available") == "on"
        sunday_available = request.POST.get("sunday_available") == "on"
        owner_name = request.POST.get("owner_name").strip()
        owner_contact = request.POST.get("owner_contact").strip()
        email = request.POST.get("email").strip()
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        image = request.FILES.get("image")
        provider_id = request.session.get('provider_id')
        provider = get_object_or_404(Service_Provider, id=provider_id)
        if Supermarket.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert('Email already exists!');window.location.href="/service_provider_add_supermarket";</script>''')
        if Supermarket.objects.filter(username=username).exists():
            return HttpResponse('''<script>alert('Username already exists. Choose a unique username');window.location.href="/service_provider_add_supermarket";</script>''')
        # Create new supermarket
        supermarket = Supermarket(
            provider=provider,
            name=name,
            location=location,
            opening_time=opening_time,
            closing_time=closing_time,
            delivery_available=delivery_available,
            is_active=True,
            sunday_available=sunday_available,
            owner_name=owner_name,
            owner_contact=owner_contact,
            email=email,
            username=username,
            password=password,
            image=image
        )
        supermarket.save()
        subject = "Your Supermarket Login Credentials"
        message = f"""
        Dear {owner_name},

        Your supermarket '{name}' has been successfully registered. Here are your login credentials:

        Username: {username}
        Password: {password}

        Please log in using these credentials and change your password after logging in.

        Regards,
        {provider.name}
        Service Provider
        """
        send_mail(subject, message, "your_email@gmail.com", [email])
        return HttpResponse('''<script>alert('Supermarket added successfully! Login details sent to email.');window.location.href="/service_provider_supermarket_list";</script>''')
    return render(request, "service_provider_add_supermarket.html")



# Service Provider Supermarket List
def service_provider_supermarket_list(request):
    provider_id = request.session.get('provider_id')
    supermarkets = Supermarket.objects.filter(provider_id=provider_id).order_by('-created_at')
    return render(request, 'service_provider_supermarket_list.html', {'supermarkets': supermarkets})



# Service Provider Edit Supermarket
def service_provider_edit_supermarket(request, supermarket_id):
    provider_id = request.session.get('provider_id')
    supermarket = get_object_or_404(Supermarket, id=supermarket_id, provider_id=provider_id)

    if request.method == 'POST':
        supermarket.name = request.POST.get('name')
        supermarket.location = request.POST.get('location')
        supermarket.opening_time = request.POST.get('opening_time')
        supermarket.closing_time = request.POST.get('closing_time')
        supermarket.delivery_available = request.POST.get('delivery_available') == 'on'
        supermarket.sunday_available = request.POST.get('sunday_available') == 'on'
        supermarket.owner_name = request.POST.get('owner_name')
        supermarket.owner_contact = request.POST.get('owner_contact')
        supermarket.email = request.POST.get('email')
        supermarket.username = request.POST.get('username')
        
        # Only update password if a new one is provided
        if password := request.POST.get('password'):
            supermarket.password = password
        
        # Update image if provided
        if 'image' in request.FILES:
            supermarket.image = request.FILES['image']
        
        # Save changes
        supermarket.save()
        
        messages.success(request, 'Supermarket details updated successfully')
        return redirect('service_provider_supermarket_list')

    return render(request, 'service_provider_supermarket_list.html', {'supermarket': supermarket})



# Service Provider Delete Supermarket
def service_provider_delete_supermarket(request, supermarket_id):
    # Get the current service provider ID from session
    provider_id = request.session.get('provider_id')
    
    # Get the supermarket, ensuring it belongs to the current provider
    supermarket = get_object_or_404(Supermarket, id=supermarket_id, provider_id=provider_id)

    if request.method == 'POST':
        supermarket.delete()
        messages.success(request, 'Supermarket deleted successfully')
        return redirect('service_provider_supermarket_list')

    return render(request, 'service_provider_supermarket_list.html', {'supermarket': supermarket})



# Service Provider Toggle Supermarket Active Status
def toggle_supermarket_status(request, supermarket_id):
    # Get the current service provider ID from session
    provider_id = request.session.get('provider_id')
    
    # Get the supermarket, ensuring it belongs to the current provider
    supermarket = get_object_or_404(Supermarket, id=supermarket_id, provider_id=provider_id)
    
    # Toggle the is_active status
    supermarket.is_active = not supermarket.is_active
    supermarket.save()
    
    status = "activated" if supermarket.is_active else "deactivated"
    messages.success(request, f'Supermarket {status} successfully')
    return redirect('service_provider_supermarket_list')



# Service Provider add Medical Store
def service_provider_add_medicalstore(request):
    if request.method == "POST":
        provider_id = request.session.get('provider_id')
        provider = get_object_or_404(Service_Provider, id=provider_id)
        
        # Get form data
        name = request.POST.get("name").strip()
        location = request.POST.get("location").strip()
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        delivery_available = request.POST.get("delivery_available") == "on"
        sunday_available = request.POST.get("sunday_available") == "on"
        owner_name = request.POST.get("owner_name").strip()
        owner_contact = request.POST.get("owner_contact").strip()
        email = request.POST.get("email").strip()
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        image = request.FILES.get("image")

        # Validate unique fields
        if MedicalStore.objects.filter(email=email).exists():
            return HttpResponse('''<script>alert('Email already exists!');window.location.href="/service_provider_add_medicalstore";</script>''')
        if MedicalStore.objects.filter(username=username).exists():
            return HttpResponse('''<script>alert('Username already exists. Choose a unique username');window.location.href="/service_provider_add_medicalstore";</script>''')

        # Create new medical store
        medicalstore = MedicalStore(
            provider=provider,
            name=name,
            location=location,
            opening_time=opening_time,
            closing_time=closing_time,
            delivery_available=delivery_available,
            is_active=True,
            sunday_available=sunday_available,
            owner_name=owner_name,
            owner_contact=owner_contact,
            email=email,
            username=username,
            password=password,
            image=image
        )
        medicalstore.save()

        # Send credentials email
        subject = "Your Medical Store Login Credentials"
        message = f"""
        Dear {owner_name},

        Your medical store '{name}' has been successfully registered. Here are your login credentials:

        Username: {username}
        Password: {password}

        Please log in using these credentials and change your password after logging in.

        Regards,
        {provider.name}
        Service Provider
        """
        send_mail(subject, message, "your_email@gmail.com", [email])
        
        return HttpResponse('''<script>alert('Medical Store added successfully! Login details sent to email.');window.location.href="/service_provider_medicalstore_list";</script>''')
    
    return render(request, "service_provider_add_medicalstore.html")



# Service Provider Medical Store List
def service_provider_medicalstore_list(request):
    provider_id = request.session.get('provider_id')
    medicalstores = MedicalStore.objects.filter(provider_id=provider_id).order_by('-created_at')
    return render(request, 'service_provider_medicalstore_list.html', {'medicalstores': medicalstores})



# Service Provider Edit Medical Store
def service_provider_edit_medicalstore(request, medicalstore_id):
    provider_id = request.session.get('provider_id')
    medicalstore = get_object_or_404(MedicalStore, id=medicalstore_id, provider_id=provider_id)

    if request.method == 'POST':
        medicalstore.name = request.POST.get('name')
        medicalstore.location = request.POST.get('location')
        medicalstore.opening_time = request.POST.get('opening_time')
        medicalstore.closing_time = request.POST.get('closing_time')
        medicalstore.delivery_available = request.POST.get('delivery_available') == 'on'
        medicalstore.sunday_available = request.POST.get('sunday_available') == 'on'
        medicalstore.owner_name = request.POST.get('owner_name')
        medicalstore.owner_contact = request.POST.get('owner_contact')
        medicalstore.email = request.POST.get('email')
        medicalstore.username = request.POST.get('username')
        
        if password := request.POST.get('password'):
            medicalstore.password = password
        
        if 'image' in request.FILES:
            medicalstore.image = request.FILES['image']
        
        medicalstore.save()
        messages.success(request, 'Medical Store details updated successfully')
        return redirect('service_provider_medicalstore_list')

    return render(request, 'service_provider_medicalstore_list.html', {'medicalstore': medicalstore})



# Service Provider Delete Medical Store
def service_provider_delete_medicalstore(request, medicalstore_id):
    provider_id = request.session.get('provider_id')
    medicalstore = get_object_or_404(MedicalStore, id=medicalstore_id, provider_id=provider_id)

    if request.method == 'POST':
        medicalstore.delete()
        messages.success(request, 'Medical Store deleted successfully')
        return redirect('service_provider_medicalstore_list')

    return render(request, 'service_provider_medicalstore_list.html', {'medicalstore': medicalstore})

# Service Provider Toggle Medical Store Active Status
def toggle_medicalstore_status(request, medicalstore_id):
    provider_id = request.session.get('provider_id')
    medicalstore = get_object_or_404(MedicalStore, id=medicalstore_id, provider_id=provider_id)
    
    medicalstore.is_active = not medicalstore.is_active
    medicalstore.save()
    
    status = "activated" if medicalstore.is_active else "deactivated"
    messages.success(request, f'Medical Store {status} successfully')
    return redirect('service_provider_medicalstore_list')



# Service provider dashboard for Order management
def service_provider_dashboard(request):
    semail = request.session.get('email')
    provider = get_object_or_404(Service_Provider, email=semail)
    
    # Get orders based on provider type
    if provider.service_type == 'Supermarket':
        orders = Order.objects.filter(product__supermarket__provider=provider)
        active_items = SupermarketProduct.objects.filter(
            supermarket__provider=provider,
            is_available=True
        ).count()
    else:  # Medical Store
        orders = Order.objects.filter(medicines__medicalstore__provider=provider)
        active_items = Medicine.objects.filter(
            medicalstore__provider=provider,
            is_available=True
        ).count()
    
    recent_orders = orders.order_by('-placed_at')[:10]
    
    context = {
        'provider': provider,
        'recent_orders': recent_orders,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='Pending').count(),
        'completed_orders': orders.filter(status='Delivered').count(),
        'active_items': active_items,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'service_provider_dashboard.html', context)



# Service provider view orders
def service_provider_orders(request):
    semail = request.session.get('email')
    provider = get_object_or_404(Service_Provider, email=semail)
    status_filter = request.GET.get('status')
    
    # Get orders based on provider type
    if provider.service_type == 'Supermarket':
        orders = Order.objects.filter(product__supermarket__provider=provider)
    else:  # Medical Store
        orders = Order.objects.filter(medicines__medicalstore__provider=provider)
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'provider': provider,
        'orders': orders.order_by('-placed_at'),
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'service_provider_orders.html', context)



# Service provider view order details
def service_provider_order_detail(request, order_id):
    semail = request.session.get('email')
    provider = get_object_or_404(Service_Provider, email=semail)
    
    order = get_object_or_404(
        Order,
        id=order_id,
        **{'product__supermarket__provider': provider} if provider.service_type == 'Supermarket' 
          else {'medicines__medicalstore__provider': provider}
    )
    status_choices = ['Pending', 'Accepted', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

    context = {
        'provider': provider,
        'order': order,
        'status_choices': status_choices,
    }
    return render(request, 'service_provider_order_detail.html', context)



# Service provider update the status of orders
def update_order_status(request, order_id):
    semail = request.session.get('email')
    provider = get_object_or_404(Service_Provider, email=semail)
    if request.method == 'POST':
        order = get_object_or_404(
            Order,
            id=order_id,
            **{'product__supermarket__provider': provider} if provider.service_type == 'Supermarket' 
              else {'medicines__medicalstore__provider': provider}
        )
        
        old_status = order.status
        # Get the status value - ensure it's a single value, not a list
        new_status = request.POST.get('status')
        if isinstance(new_status, (list, tuple)):
            new_status = new_status[0]  # Take the first item if it's a list/tuple
            
        order.status = new_status
        order.payment_status = request.POST.get('payment_status')
        order.estimated_delivery = request.POST.get('estimated_delivery') or None
        
        # Update tracking history
        notes = request.POST.get('status_notes', '')
        
        if not order.tracking_history:
            order.tracking_history = {'entries': []}
        
        if 'entries' not in order.tracking_history:
            order.tracking_history['entries'] = []
            
        import datetime
        order.tracking_history['entries'].append({
            'status': order.status,
            'timestamp': datetime.datetime.now().isoformat(),
            'notes': notes
        })
        
        order.save()
        
        if request.POST.get('send_email') == 'on':
            send_order_status_email(order, old_status, notes)
            
        messages.success(request, f'Order #{order_id} has been updated successfully.')
    
    return redirect('service_provider_orders')



# Service provider send mail for update status
def send_order_status_email(order, old_status, notes):
    """
    Send email notification to customer about order status change
    """
    if old_status == order.status:
        return  # No email if status didn't change
    
    subject = f"Order #{order.id} status updated to {order.status}"
    
    # Email content
    message = f"""
    Hello {order.user.full_name},
    
    Your order #{order.id} status has been updated:
    
    Previous status: {old_status}
    New status: {order.status}
    
    {f"Estimated delivery: {order.estimated_delivery}" if order.estimated_delivery else ""}
    
    {f"Notes: {notes}" if notes else ""}
    
    Thank you for your business!
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=True,
    )



# Helper function to get service provider from session
def get_service_provider(request):
    if 'email' in request.session:
        try:
            return Service_Provider.objects.get(email=request.session['email'])
        except Service_Provider.DoesNotExist:
            return None
    return None



# Service provider facility management dashboard
def service_provider_facility_management(request):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Get facilities managed by this service provider
    facilities = Facility.objects.filter(facility_type=service_provider.service_type)
    bookings = FacilityBooking.objects.filter(
        facility__facility_type=service_provider.service_type,
        booking_date__gte=date.today()
    ).order_by('booking_date', 'start_time')[:5]
    
    context = {
        'service_provider': service_provider,
        'facility_count': facilities.count(),
        'upcoming_bookings': bookings,
    }
    return render(request, 'service_provider_facility_management.html', context)



# Service provider facility list
def service_provider_facilities(request):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facilities = Facility.objects.filter(facility_type=service_provider.service_type)
    context = {
        'facilities': facilities,
        'service_type': service_provider.service_type,
    }
    return render(request, 'service_provider_facilities.html', context)



# Service provider add facility 
def add_facility(request):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    if request.method == 'POST':
        try:
            facility = Facility(
                name=request.POST.get('name'),
                facility_type=service_provider.service_type,
                location=request.POST.get('location'),
                description=request.POST.get('description', ''),
                opening_time=request.POST.get('opening_time'),
                closing_time=request.POST.get('closing_time'),
                max_capacity=int(request.POST.get('max_capacity')),
                rules=request.POST.get('rules', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            if 'image' in request.FILES:
                facility.image = request.FILES['image']
            facility.save()
            messages.success(request, 'Facility added successfully!')
            return redirect('service_provider_facilities')
        except Exception as e:
            messages.error(request, f'Error adding facility: {str(e)}')
    
    context = {
        'service_type': service_provider.service_type,
    }
    return render(request, 'add_facility.html', context)



# Service provider edit facility 
def edit_facility(request, facility_id):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facility = get_object_or_404(Facility, id=facility_id, facility_type=service_provider.service_type)
    
    if request.method == 'POST':
        try:
            facility.name = request.POST.get('name')
            facility.location = request.POST.get('location')
            facility.description = request.POST.get('description', '')
            facility.opening_time = request.POST.get('opening_time')
            facility.closing_time = request.POST.get('closing_time')
            facility.max_capacity = int(request.POST.get('max_capacity'))
            facility.rules = request.POST.get('rules', '')
            facility.is_active = request.POST.get('is_active') == 'on'
            if 'image' in request.FILES:
                facility.image = request.FILES['image']
            facility.save()
            messages.success(request, 'Facility updated successfully!')
            return redirect('service_provider_facilities')
        except Exception as e:
            messages.error(request, f'Error updating facility: {str(e)}')
    
    context = {
        'facility': facility,
    }
    return render(request, 'edit_facility.html', context)



# Service provider delete facility 
def delete_facility(request, facility_id):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    facility = get_object_or_404(Facility, id=facility_id, facility_type=service_provider.service_type)
    
    if request.method == 'POST':
        try:
            facility.delete()
            messages.success(request, 'Facility deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting facility: {str(e)}')
        return redirect('service_provider_facilities')
    
    context = {
        'facility': facility,
    }
    return render(request, 'delete_facility.html', context)



# Service provider view facility bookings 
def service_provider_bookings(request):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Get all bookings for facilities managed by this service provider
    bookings = FacilityBooking.objects.filter(
        facility__facility_type=service_provider.service_type
    ).order_by('-booking_date', '-start_time')
    
    # Filtering
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if date_filter:
        bookings = bookings.filter(booking_date=date_filter)
    
    context = {
        'bookings': bookings,
        'status_choices': FacilityBooking.STATUS_CHOICES,
    }
    return render(request, 'service_provider_bookings.html', context)



# Service provider facility booking management 
def update_booking_status(request, booking_id):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    booking = get_object_or_404(
        FacilityBooking, 
        id=booking_id,
        facility__facility_type=service_provider.service_type
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in [choice[0] for choice in FacilityBooking.STATUS_CHOICES]:
            booking.status = new_status
            booking.notes = notes
            booking.save()
            messages.success(request, f'Booking status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status selected')
        
        return redirect('service_provider_bookings')
    
    context = {
        'booking': booking,
        'status_choices': FacilityBooking.STATUS_CHOICES,
    }
    return render(request, 'update_booking_status.html', context)



# Service provider facility usage log
def facility_usage_logs(request):
    service_provider = get_service_provider(request)
    if not service_provider:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')
    
    # Get bookings for facilities of the service provider's type
    bookings = FacilityBooking.objects.filter(
        facility__facility_type=service_provider.service_type
    ).order_by('-created_at')
    
    # Calculate duration for each booking
    booking_data = []
    for booking in bookings:
        duration = None
        if booking.start_time and booking.end_time:
            start_dt = datetime.combine(booking.booking_date, booking.start_time)
            end_dt = datetime.combine(booking.booking_date, booking.end_time)
            duration = end_dt - start_dt
            
        booking_data.append({
            'booking': booking,
            'duration': duration
        })
    
    context = {
        'booking_data': booking_data,
        'service_provider': service_provider,
    }
    return render(request, 'facility_usage_logs.html', context)



# For Service Providers
def submit_sp_complaint(request):
    user_type = get_user_type(request)
    if user_type != 'service_provider':
        messages.error(request, "You need to login as a service provider to submit complaints")
        return redirect('login')
    
    service_provider = Service_Provider.objects.get(email=request.session['email'])
    
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint')
        Complaints.objects.create(
            service_provider=service_provider,
            complaint=complaint_text,
            status='Pending'
        )
        messages.success(request, "Complaint submitted successfully!")
        return redirect('view_sp_complaints')
    
    return render(request, 'submit_sp_complaint.html')

def view_sp_complaints(request):
    user_type = get_user_type(request)
    if user_type != 'service_provider':
        messages.error(request, "Access denied")
        return redirect('login')
    
    service_provider = Service_Provider.objects.get(email=request.session['email'])
    complaints = Complaints.objects.filter(service_provider=service_provider).order_by('-created_at')
    
    return render(request, 'sp_complaints.html', {'complaints': complaints})





#################################################    MEDICAL STORE    ####################################################





# Medical store login
def medical_store_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if MedicalStore.objects.filter(username=username, password=password).exists():
            medical_store = MedicalStore.objects.get(username=username)
            request.session['email'] = medical_store.email
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/medical_store_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/medical_store_login/";</script>''')
    return render(request,'medical_store_login.html')



# Medical store home
def medical_store_home(request):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    email = request.session['email']
    medical_store = MedicalStore.objects.get(email=email)
    return render(request,'medical_store_home.html', {'medical_store': medical_store})



# Medical store add medicines
def medical_store_add_medicines(request):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    
    if request.method == 'POST':
        email = request.session['email']
        medical_store = MedicalStore.objects.get(email=email)
        
        name = request.POST.get('name')
        description = request.POST.get('description')
        manufacturer = request.POST.get('manufacturer')
        expiry_date = request.POST.get('expiry_date')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        
        medicine = Medicine(
            medicalstore=medical_store,
            name=name,
            description=description,
            manufacturer=manufacturer,
            expiry_date=expiry_date,
            price=price,
            stock=stock,
            image=image
        )
        medicine.save()
        return HttpResponse('''<script>alert('Medicine Added Successfully');window.location.href="/medical_store_view_medicines/";</script>''')
    
    return render(request, 'medical_store_add_medicines.html')



# Medical store view medicine list
def medical_store_view_medicines(request):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    
    email = request.session['email']
    medical_store = MedicalStore.objects.get(email=email)
    medicines = Medicine.objects.filter(medicalstore=medical_store)
    
    return render(request, 'medical_store_view_medicines.html', {'medicines': medicines})



# Medical store edit medicine
def medical_store_edit_medicine(request, medicine_id):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    
    medicine = Medicine.objects.get(id=medicine_id)
    
    if request.method == 'POST':
        medicine.name = request.POST.get('name')
        medicine.description = request.POST.get('description')
        medicine.manufacturer = request.POST.get('manufacturer')
        medicine.expiry_date = request.POST.get('expiry_date')
        medicine.price = request.POST.get('price')
        medicine.stock = request.POST.get('stock')
        
        if 'image' in request.FILES:
            medicine.image = request.FILES['image']
        
        medicine.save()
        return HttpResponse('''<script>alert('Medicine Updated Successfully');window.location.href="/medical_store_view_medicines/";</script>''')
    
    return render(request, 'medical_store_edit_medicine.html', {'medicine': medicine})



# Medical store delete medicines
def medical_store_delete_medicine(request, medicine_id):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    
    medicine = Medicine.objects.get(id=medicine_id)
    medicine.delete()
    return HttpResponse('''<script>alert('Medicine Deleted Successfully');window.location.href="/medical_store_view_medicines/";</script>''')



# Medical store profile view
def medical_store_profile(request):
    if 'email' not in request.session:
        return redirect('/medical_store_login/')
    
    email = request.session['email']
    medical_store = MedicalStore.objects.get(email=email)
    
    if request.method == 'POST':
        medical_store.name = request.POST.get('name')
        medical_store.location = request.POST.get('location')
        medical_store.opening_time = request.POST.get('opening_time')
        medical_store.closing_time = request.POST.get('closing_time')
        medical_store.delivery_available = 'delivery_available' in request.POST
        medical_store.sunday_available = 'sunday_available' in request.POST
        medical_store.owner_name = request.POST.get('owner_name')
        medical_store.owner_contact = request.POST.get('owner_contact')
        
        if 'image' in request.FILES:
            medical_store.image = request.FILES['image']
        
        medical_store.save()
        return HttpResponse('''<script>alert('Profile Updated Successfully');window.location.href="/medical_store_profile/";</script>''')
    
    return render(request, 'medical_store_profile.html', {'medical_store': medical_store})



# Medical Store order management dashboard
def medicalstore_dashboard(request):
    semail = request.session.get('email')
    medicalstore = get_object_or_404(MedicalStore, email=semail)
    
    orders = Order.objects.filter(medicines__medicalstore=medicalstore).order_by('-placed_at')
    medicines = Medicine.objects.filter(medicalstore=medicalstore, is_available=True)
    
    # Calculate today's revenue
    today_revenue = orders.filter(placed_at__date=timezone.now().date()).aggregate(
        sum=Sum('price')
    )['sum'] or 0
    
    context = {
        'medicalstore': medicalstore,
        'orders': orders,  # Pass the full queryset if needed
        'recent_orders': orders[:5],
        'total_orders': orders.count(),
        'active_medicines': medicines.count(),
        'pending_orders_count': orders.filter(status='Pending').count(),
        'completed_orders': orders.filter(status='Delivered').count(),
        'status_choices': Order.STATUS_CHOICES,
        'today_revenue': today_revenue,
        'now': timezone.now(),
    }
    return render(request, 'medicalstore_dashboard.html', context)



# Medical Store view orders
def medicalstore_orders(request):
    semail = request.session.get('email')
    medicalstore = get_object_or_404(MedicalStore, email=semail)
    
    orders = Order.objects.filter(medicines__medicalstore=medicalstore)
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    status_choices = ['Pending', 'Accepted', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

    context = {
        'medicalstore': medicalstore,
        'orders': orders.order_by('-placed_at'),
        'status_filter': status_filter,
        'status_choices': status_choices,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'medicalstore_orders.html', context)



# Medical Store view order details
def medicalstore_order_detail(request, order_id):
    semail = request.session.get('email')
    medicalstore = get_object_or_404(MedicalStore, email=semail)
    
    order = get_object_or_404(
        Order,
        id=order_id,
        medicines__medicalstore=medicalstore
    )
    status_choices = ['Pending', 'Accepted', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    context = {
        'medicalstore': medicalstore,
        'order': order,
        'status_choices': status_choices,
    }
    return render(request, 'medicalstore_order_detail.html', context)




#################################################     SUPERMARKET    ####################################################





# Supermarket login
def supermarket_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Supermarket.objects.filter(username=username, password=password).exists():
            supermarket = Supermarket.objects.get(username=username)
            request.session['email'] = supermarket.email
            return HttpResponse('''<script>alert('Login Successful');window.location.href="/supermarket_home/";</script>''')
        else:
            return HttpResponse('''<script>alert('Login Failed');window.location.href="/supermarket_login/";</script>''')
    return render(request,'supermarket_login.html')



# Supermarket Home
def supermarket_home(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    return render(request, 'supermarket_home.html', {'supermarket': supermarket})



# Supermarket add categories
def supermarket_add_category(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    if request.method == 'POST':
        email = request.session['email']
        supermarket = Supermarket.objects.get(email=email)
        
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        category = ProductCategory(
            supermarket=supermarket,
            name=name,
            description=description
        )
        category.save()
        return HttpResponse('''<script>alert('Category Added Successfully');window.location.href="/supermarket_view_categories/";</script>''')
    
    return render(request, 'supermarket_add_category.html')



# Supermarket view category list
def supermarket_view_categories(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    categories = ProductCategory.objects.filter(supermarket=supermarket)
    
    return render(request, 'supermarket_view_categories.html', {'categories': categories})



# Supermarket edit category 
def supermarket_edit_category(request, category_id):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    category = ProductCategory.objects.get(id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        return HttpResponse('''<script>alert('Category Updated Successfully');window.location.href="/supermarket_view_categories/";</script>''')
    
    return render(request, 'supermarket_edit_category.html', {'category': category})



# Supermarket delete category 
def supermarket_delete_category(request, category_id):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    category = ProductCategory.objects.get(id=category_id)
    category.delete()
    return HttpResponse('''<script>alert('Category Deleted Successfully');window.location.href="/supermarket_view_categories/";</script>''')



# Supermarket add products
def supermarket_add_product(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    categories = ProductCategory.objects.filter(supermarket=supermarket)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        
        category = ProductCategory.objects.get(id=category_id) if category_id else None
        
        product = SupermarketProduct(
            supermarket=supermarket,
            category=category,
            name=name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )
        product.save()
        return HttpResponse('''<script>alert('Product Added Successfully');window.location.href="/supermarket_view_products/";</script>''')
    
    return render(request, 'supermarket_add_product.html', {'categories': categories})



# Supermarket view products list
def supermarket_view_products(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    products = SupermarketProduct.objects.filter(supermarket=supermarket)
    
    return render(request, 'supermarket_view_products.html', {'products': products})



# Supermarket edit product
def supermarket_edit_product(request, product_id):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    product = SupermarketProduct.objects.get(id=product_id)
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    categories = ProductCategory.objects.filter(supermarket=supermarket)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        category_id = request.POST.get('category')
        product.category = ProductCategory.objects.get(id=category_id) if category_id else None
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        return HttpResponse('''<script>alert('Product Updated Successfully');window.location.href="/supermarket_view_products/";</script>''')
    
    return render(request, 'supermarket_edit_product.html', {
        'product': product,
        'categories': categories
    })



# Supermarket delete product
def supermarket_delete_product(request, product_id):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    product = SupermarketProduct.objects.get(id=product_id)
    product.delete()
    return HttpResponse('''<script>alert('Product Deleted Successfully');window.location.href="/supermarket_view_products/";</script>''')



# Supermarket Profile view
def supermarket_profile(request):
    if 'email' not in request.session:
        return redirect('/supermarket_login/')
    
    email = request.session['email']
    supermarket = Supermarket.objects.get(email=email)
    
    if request.method == 'POST':
        supermarket.name = request.POST.get('name')
        supermarket.location = request.POST.get('location')
        supermarket.opening_time = request.POST.get('opening_time')
        supermarket.closing_time = request.POST.get('closing_time')
        supermarket.delivery_available = 'delivery_available' in request.POST
        supermarket.sunday_available = 'sunday_available' in request.POST
        supermarket.owner_name = request.POST.get('owner_name')
        supermarket.owner_contact = request.POST.get('owner_contact')
        
        if 'image' in request.FILES:
            supermarket.image = request.FILES['image']
        
        supermarket.save()
        return HttpResponse('''<script>alert('Profile Updated Successfully');window.location.href="/supermarket_profile/";</script>''')
    
    return render(request, 'supermarket_profile.html', {'supermarket': supermarket})



# Supermarket Order management dashboard
def supermarket_dashboard(request):
    semail = request.session.get('email')
    supermarket = get_object_or_404(Supermarket, email=semail)
    
    orders = Order.objects.filter(product__supermarket=supermarket).order_by('-placed_at')
    products = SupermarketProduct.objects.filter(supermarket=supermarket, is_available=True)
    # Calculate today's revenue
    today_revenue = orders.filter(placed_at__date=timezone.now().date()).aggregate(
        sum=Sum('price')
    )['sum'] or 0
    
    context = {
        'supermarket': supermarket,
        'orders': orders,  # Pass the full queryset if needed
        'recent_orders': orders[:5],
        'total_orders': orders.count(),
        'active_products': products.count(),
        'status_choices': Order.STATUS_CHOICES,
        'pending_orders_count': orders.filter(status='Pending').count(),
        'completed_orders': orders.filter(status='Delivered').count(),
        'status_choices': Order.STATUS_CHOICES,
        'today_revenue': today_revenue,
        'now': timezone.now(),
    }
    return render(request, 'supermarket_dashboard.html', context)



# Supermarket view orders
def supermarket_orders(request):
    semail = request.session.get('email')
    supermarket = get_object_or_404(Supermarket, email=semail)
    
    orders = Order.objects.filter(product__supermarket=supermarket)
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    status_choices = ['Pending', 'Accepted', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

    context = {
        'supermarket': supermarket,
        'orders': orders.order_by('-placed_at'),
        'status_filter': status_filter,
        'status_choices': status_choices,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'supermarket_orders.html', context)



# Supermarket view order details
def supermarket_order_detail(request, order_id):
    semail = request.session.get('email')
    supermarket = get_object_or_404(Supermarket, email=semail)
    
    order = get_object_or_404(
        Order,
        id=order_id,
        product__supermarket=supermarket
    )
    status_choices = ['Pending', 'Accepted', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    context = {
        'supermarket': supermarket,
        'order': order,
        'status_choices': status_choices,
    }
    return render(request, 'supermarket_order_detail.html', context)






# Chat between flat occupant and security
def chat_list(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        if FlatOccupant.objects.filter(email=request.session['email']).exists():
            user = FlatOccupant.objects.get(email=request.session['email'])
            user_type = 'occupant'
            # Get all security personnel for occupant to select
            security_list = Security.objects.all()
            # Get chat rooms where this occupant is involved
            chat_rooms = ChatRoom.objects.filter(occupant=user).order_by('-last_message_time')
        elif Security.objects.filter(email=request.session['email']).exists():
            user = Security.objects.get(email=request.session['email'])
            user_type = 'security'
            # Get all occupants for security to select
            occupant_list = FlatOccupant.objects.filter(is_active=True)
            # Get chat rooms where this security is involved
            chat_rooms = ChatRoom.objects.filter(security=user).order_by('-last_message_time')
        else:
            messages.error(request, "Invalid user session")
            return redirect('login')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('login')
    
    return render(request, 'chat_list.html', {
        'user': user,
        'user_type': user_type,
        'chat_rooms': chat_rooms,
        'security_list': security_list if user_type == 'occupant' else None,
        'occupant_list': occupant_list if user_type == 'security' else None,
    })

def chat_room(request, room_id):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # Verify user has access to this chat room
        if FlatOccupant.objects.filter(email=request.session['email']).exists():
            occupant = FlatOccupant.objects.get(email=request.session['email'])
            if chat_room.occupant != occupant:
                messages.error(request, "You don't have access to this chat")
                return redirect('chat_list')
            user_type = 'occupant'
            other_user = chat_room.security
        elif Security.objects.filter(email=request.session['email']).exists():
            security = Security.objects.get(email=request.session['email'])
            if chat_room.security != security:
                messages.error(request, "You don't have access to this chat")
                return redirect('chat_list')
            user_type = 'security'
            other_user = chat_room.occupant
        else:
            messages.error(request, "Invalid user session")
            return redirect('login')
        
        if request.method == 'POST':
            content = request.POST.get('content')
            attachment = request.FILES.get('attachment')
            
            if content or attachment:
                sender_type = 'Occupant' if user_type == 'occupant' else 'Security'
                sender_id = occupant.id if user_type == 'occupant' else security.id
                
                Message.objects.create(
                    chat_room=chat_room,
                    sender_type=sender_type,
                    sender_id=sender_id,
                    content=content,
                    attachment=attachment
                )
                
                # Update last message time
                chat_room.last_message_time = timezone.now()
                chat_room.save()
                
                return redirect('chat_room', room_id=room_id)
        
        # Mark messages as read
        Message.objects.filter(
            chat_room=chat_room,
            is_read=False
        ).exclude(
            sender_type=user_type.capitalize()
        ).update(is_read=True)
        
        messages = chat_room.messages.all().order_by('created_at')
        
        return render(request, 'chat_room.html', {
            'chat_room': chat_room,
            'messages': messages,
            'user_type': user_type,
            'other_user': other_user,
        })
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('chat_list')

def start_chat(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        if request.method == 'POST':
            if FlatOccupant.objects.filter(email=request.session['email']).exists():
                occupant = FlatOccupant.objects.get(email=request.session['email'])
                security_id = request.POST.get('security_id')
                security = get_object_or_404(Security, id=security_id)
                
                # Check if chat room already exists
                chat_room, created = ChatRoom.objects.get_or_create(
                    security=security,
                    occupant=occupant,
                    defaults={'last_message_time': timezone.now()}
                )
                
                return redirect('chat_room', room_id=chat_room.id)
                
            elif Security.objects.filter(email=request.session['email']).exists():
                security = Security.objects.get(email=request.session['email'])
                occupant_id = request.POST.get('occupant_id')
                occupant = get_object_or_404(FlatOccupant, id=occupant_id)
                
                # Check if chat room already exists
                chat_room, created = ChatRoom.objects.get_or_create(
                    security=security,
                    occupant=occupant,
                    defaults={'last_message_time': timezone.now()}
                )
                
                return redirect('chat_room', room_id=chat_room.id)
                
        return redirect('chat_list')
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('chat_list')



def product_detail(request, item_id):
    product = get_object_or_404(SupermarketProduct, id=item_id)
    return render(request, 'product_detail.html', {'product': product})

def medicine_detail(request, item_id):
    medicine = get_object_or_404(Medicine, id=item_id)
    return render(request, 'medicine_detail.html', {'medicine': medicine})

# User view
def view_notifications(request):
    notifications = Notification.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'user_notifications.html', {'notifications': notifications})








