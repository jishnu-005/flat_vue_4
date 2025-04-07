from django.db import models
from django.utils import timezone
import random
import string

# Create your models here.

class Security(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField()  
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  
    address = models.TextField()
    shift_timing = models.CharField(max_length=50, choices=[('Morning', 'Morning'), ('Night', 'Night')])
    profile_image = models.ImageField(upload_to='security_profiles/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name
 
class Service_Provider(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    SERVICE_CHOICES = [
        ('Gym', 'Gym'),
        ('Swimming Pool', 'Swimming Pool'),
        ('Medical Store', 'Medical Store'),
        ('Supermarket', 'Supermarket'),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField()  
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  
    address = models.TextField()
    profile_image = models.ImageField(upload_to='service_provider_profiles/', blank=True, null=True) 
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.name} - {self.service_type}"
    
class Flat(models.Model):
    flat_number = models.CharField(max_length=20, unique=True)
    floor = models.IntegerField()
    block = models.CharField(max_length=10, blank=True, null=True)
    square_footage = models.PositiveIntegerField(blank=True, null=True)
    bedrooms = models.PositiveIntegerField(default=1)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['block', 'floor', 'flat_number']
    
    def __str__(self):
        block_str = f"Block {self.block} - " if self.block else ""
        return f"{block_str}Floor {self.floor} - Flat {self.flat_number}"
    
class FlatOccupant(models.Model):
    OCCUPANT_TYPE_CHOICES = [
        ('Owner', 'Owner'),
        ('Tenant', 'Tenant'),
    ]

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name="occupant")
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    occupant_type = models.CharField(max_length=10, choices=OCCUPANT_TYPE_CHOICES)
    move_in_date = models.DateField()
    move_out_date = models.DateField(blank=True, null=True) 
    id_proof = models.ImageField(upload_to='id_proofs/', blank=True, null=True)  
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.flat.flat_number}"

class Visitor(models.Model):
    VISITOR_TYPE_CHOICES = [
        ('Expected', 'Expected'),
        ('Unexpected', 'Unexpected'),
        ('Delivery', 'Delivery'),
        ('Service', 'Service'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('CheckedIn', 'Checked In'),
        ('CheckedOut', 'Checked Out'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPE_CHOICES)
    purpose = models.TextField(blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    id_proof_type = models.CharField(max_length=50, blank=True, null=True)
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)
    id_proof_image = models.ImageField(upload_to='visitor_ids/', blank=True, null=True)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, null=True, blank=True)
    requested_by = models.ForeignKey(FlatOccupant, on_delete=models.SET_NULL, null=True, blank=True)
    expected_arrival = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    actual_departure = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(Security, on_delete=models.SET_NULL, 
                                    related_name='checked_in_visitors', null=True, blank=True)
    checked_out_by = models.ForeignKey(Security, on_delete=models.SET_NULL, 
                                     related_name='checked_out_visitors', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_unexpected = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.verification_code and self.visitor_type == 'Expected':
            self.verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_visitor_type_display()} - {self.status}"



class ChatRoom(models.Model):
    # A unique identifier for each chat room between security and occupant
    security = models.ForeignKey('Security', on_delete=models.CASCADE, related_name='chat_rooms')
    occupant = models.ForeignKey('FlatOccupant', on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('security', 'occupant')
        ordering = ['-last_message_time']
    
    def __str__(self):
        return f"Chat between {self.security.name} and {self.occupant.full_name}"

class Message(models.Model):
    SENDER_TYPE_CHOICES = [
        ('Security', 'Security'),
        ('Occupant', 'Occupant'),
    ]
    
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_id = models.IntegerField()  # ID of either Security or FlatOccupant
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender_type} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Facility(models.Model):
    FACILITY_TYPES = [
        ('Gym', 'Gym'),
        ('Swimming Pool', 'Swimming Pool'),
    ]
    
    name = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    max_capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='facility_images/', blank=True, null=True)
    rules = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"

class FacilityBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(FlatOccupant, on_delete=models.CASCADE, related_name='facility_bookings')
    service_provider = models.ForeignKey(Service_Provider, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    purpose = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    checked_in = models.BooleanField(default=False)
    checked_in_time = models.DateTimeField(null=True, blank=True)
    checked_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ['booking_date', 'start_time']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.facility.name} on {self.booking_date}"

class FacilityUsageLog(models.Model):
    booking = models.OneToOneField(FacilityBooking, on_delete=models.CASCADE, related_name='usage_log')
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Usage log for {self.booking}"
    

class Supermarket(models.Model):
    provider = models.ForeignKey(Service_Provider, on_delete=models.CASCADE, related_name='supermarket_provider')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    delivery_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sunday_available = models.BooleanField(default=False)   
    owner_name = models.CharField(max_length=100)
    owner_contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='supermarket_images/', blank=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.provider.username}"


class ProductCategory(models.Model):
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SupermarketProduct(models.Model):
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='supermarket_products/', blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.supermarket.name})"


class MedicalStore(models.Model):
    provider = models.ForeignKey(Service_Provider, on_delete=models.CASCADE, related_name='medicalstore_provider')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    delivery_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sunday_available = models.BooleanField(default=False)   
    owner_name = models.CharField(max_length=100)
    owner_contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='supermarket_images/', blank=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.provider.username}"

class Medicine(models.Model):
    medicalstore = models.ForeignKey(MedicalStore, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100)  # New field: Manufacturer name
    expiry_date = models.DateField()  # New field: Expiry date of the medicine
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.medicalstore.name}"

class Cart(models.Model):
    user = models.ForeignKey(FlatOccupant, on_delete=models.CASCADE)
    product = models.ForeignKey(SupermarketProduct, on_delete=models.CASCADE,blank=True,null=True)
    medicines = models.ForeignKey(Medicine, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.product.name} (x{self.quantity})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Processing', 'Processing'),
        ('Dispatched', 'Dispatched'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(FlatOccupant, on_delete=models.CASCADE, related_name='orders',blank=True,null=True)  
    product = models.ForeignKey(SupermarketProduct, on_delete=models.CASCADE,blank=True,null=True)
    medicines = models.ForeignKey(Medicine, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending',blank=True,null=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    tracking_history = models.JSONField(default=dict)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(FlatOccupant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"



class Complaints(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]
    
    flat_occupant = models.ForeignKey(FlatOccupant, on_delete=models.CASCADE, blank=True, null=True)
    service_provider = models.ForeignKey(Service_Provider, on_delete=models.CASCADE, blank=True, null=True)
    complaint = models.TextField()
    reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read_by_admin = models.BooleanField(default=False)
    is_read_by_user = models.BooleanField(default=False)

    def __str__(self):
        if self.flat_occupant:
            return f"Complaint from {self.flat_occupant.full_name}"
        return f"Complaint from {self.service_provider.name}"

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

   














