from django.urls import path
from .import views
urlpatterns = [


    path('',views.index,name='index'),
    path('logout/',views.logout,name='logout'),


    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_home/',views.admin_home,name='admin_home'),
    path('admin_add_flat/', views.admin_add_flat, name='admin_add_flat'),
    path('admin_flat_list/', views.admin_flat_list, name='admin_flat_list'),
    path('admin_edit_flat/<int:flat_id>/', views.admin_edit_flat, name='admin_edit_flat'),
    path('admin_delete_flat/<int:flat_id>/', views.admin_delete_flat, name='admin_delete_flat'),
    path('admin_add_security/', views.admin_add_security, name='admin_add_security'),
    path('admin_security_list/', views.admin_security_list, name='admin_security_list'),
    path('admin_edit_security/<int:security_id>/', views.admin_edit_security, name='admin_edit_security'),
    path('admin_delete_security/<int:security_id>/', views.admin_delete_security, name='admin_delete_security'),
    path('admin_add_flat_occupant/', views.admin_add_flat_occupant, name='admin_add_flat_occupant'),
    path('admin_flat_occupant_list/', views.admin_flat_occupant_list, name='admin_flat_occupant_list'),
    path('admin_edit_flat_occupant/<int:occupant_id>/', views.admin_edit_flat_occupant, name='admin_edit_flat_occupant'),
    path('admin_delete_flat_occupant/<int:occupant_id>/', views.admin_delete_flat_occupant, name='admin_delete_flat_occupant'),
    path('admin_add_service_provider/', views.admin_add_service_provider, name='admin_add_service_provider'),
    path('admin_service_provider_list/', views.admin_service_provider_list, name='admin_service_provider_list'),
    path('admin_edit_service_provider/<int:provider_id>/', views.admin_edit_service_provider, name='admin_edit_service_provider'),
    path('admin_delete_service_provider/<int:provider_id>/', views.admin_delete_service_provider, name='admin_delete_service_provider'),
    path('notification_list/', views.notification_list, name='notification_list'),
    path('add_notification/add/', views.add_notification, name='add_notification'),
    path('edit_notification/<int:id>/', views.edit_notification, name='edit_notification'),
    path('delete_notification/<int:id>/', views.delete_notification, name='delete_notification'),
    path('admin_visitor_list/', views.admin_visitor_list, name='admin_visitor_list'),
    path('admin_visitor_detail/<int:id>/', views.admin_visitor_detail, name='admin_visitor_detail'),
    path('all_complaints/', views.all_complaints, name='all_complaints'),
    path('complaint_detail/<int:id>/', views.complaint_detail, name='complaint_detail'),
    



    path('flat_occupant_login/',views.flat_occupant_login,name='flat_occupant_login'),
    path('flat_occupant_home/',views.flat_occupant_home,name='flat_occupant_home'),
    path('flat_occupant_profile/',views.flat_occupant_profile,name='flat_occupant_profile'),
    path('flat_occupant_supermarket_list/', views.flat_occupant_supermarket_list, name='flat_occupant_supermarket_list'),
    path('flat_occupant_supermarket_products/<int:supermarket_id>/', views.flat_occupant_supermarket_products, name='flat_occupant_supermarket_products'),
    path('flat_occupant_products/<int:product_id>/', views.flat_occupant_products, name='flat_occupant_products'),
    path('flat_occupant_product_list/', views.flat_occupant_product_list, name='flat_occupant_product_list'),
    path('flat_occupant_medicalstore_list/', views.flat_occupant_medicalstore_list, name='flat_occupant_medicalstore_list'),
    path('flat_occupant_medicalstore_medicines/<int:medicalstore_id>/',views.flat_occupant_medicalstore_medicines,name='flat_occupant_medicalstore_medicines'),
    path('flat_occupant_medicine_detail/<int:medicine_id>/',views.flat_occupant_medicine_detail, name='flat_occupant_medicine_detail'),
    path('flat_occupant_medicine_list/', views.flat_occupant_medicine_list, name='flat_occupant_medicine_list'),
    path('flat_occupant_add_to_cart/<str:item_type>/<int:item_id>/', views.flat_occupant_add_to_cart, name='add_to_cart'),
    path('flat_occupant_cart_view/', views.flat_occupant_cart_view, name='flat_occupant_cart_view'),
    path('flat_occupant_remove_from_cart/',  views.flat_occupant_remove_from_cart, name='remove_from_cart'),
    path('flat_occupant_update_cart/',   views.flat_occupant_update_cart,  name='update_cart'),
    path('flat_occupant_place_order/', views.flat_occupant_place_order, name='place_order'),
    path('flat_occupant_orders/', views.flat_occupant_orders, name='flat_occupant_orders'),
    path('create_razorpay_order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify_razorpay_payment/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('resident_dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('resident/add-visitor/', views.add_expected_visitor, name='add_expected_visitor'),
    path('resident_visitor_history/', views.resident_visitor_history, name='resident_visitor_history'),
    path('facilities/', views.facility_list, name='facility_list'),
    path('facility_detail/<int:facility_id>/', views.facility_detail, name='facility_detail'),
    path('book_facility/<int:facility_id>/', views.book_facility, name='book_facility'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('check_in/<int:booking_id>/', views.check_in, name='check_in'),
    path('check_out/<int:booking_id>/', views.check_out, name='check_out'),
    path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
    path('view_my_complaints/', views.view_my_complaints, name='view_my_complaints'),


    
    path('security_login/',views.security_login,name='security_login'),
    path('security_home/',views.security_home,name='security_home'),
    path('security_dashboard/', views.security_dashboard, name='security_dashboard'),
    path('security/unexpected/', views.handle_unexpected_visitor, name='handle_unexpected_visitor'),
    path('security/check-in/', views.check_in_visitor, name='check_in_visitor'),
    path('security/check-out/<int:visitor_id>/', views.check_out_visitor, name='check_out_visitor'),
    path('security_visitor_history/', views.security_visitor_history, name='security_visitor_history'),


    path('service_provider_login/',views.service_provider_login,name='service_provider_login'),
    path('service_provider_home/',views.service_provider_home,name='service_provider_home'),
    path('service_provider_add_supermarket/', views.service_provider_add_supermarket, name='service_provider_add_supermarket'),
    path('service_provider_supermarket_list/', views.service_provider_supermarket_list, name='service_provider_supermarket_list'),
    path('service_provider_edit_supermarket/<int:supermarket_id>/', views.service_provider_edit_supermarket, name='service_provider_edit_supermarket'),
    path('service_provider_delete_supermarket/<int:supermarket_id>/', views.service_provider_delete_supermarket, name='service_provider_delete_supermarket'),
    path('toggle_supermarket_status/<int:supermarket_id>/', views.toggle_supermarket_status, name='toggle_supermarket_status'),
    path('service_provider_add_medicalstore/', views.service_provider_add_medicalstore, name='service_provider_add_medicalstore'),
    path('service_provider_medicalstore_list/', views.service_provider_medicalstore_list, name='service_provider_medicalstore_list'),
    path('service_provider_edit_medicalstore/<int:medicalstore_id>/', views.service_provider_edit_medicalstore, name='service_provider_edit_medicalstore'),
    path('service_provider_delete_medicalstore/<int:medicalstore_id>/', views.service_provider_delete_medicalstore, name='service_provider_delete_medicalstore'),
    path('toggle_medicalstore_status/<int:medicalstore_id>/', views.toggle_medicalstore_status, name='toggle_medicalstore_status'),
    path('service_provider_dashboard/', views.service_provider_dashboard, name='service_provider_dashboard'),
    path('service_provider_orders/', views.service_provider_orders, name='service_provider_orders'),
    path('service_provider_order_detail/<int:order_id>/', views.service_provider_order_detail, name='service_provider_order_detail'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('service_provider_facility_management/', views.service_provider_facility_management, name='service_provider_facility_management'),
    path('service_provider_facilities/', views.service_provider_facilities, name='service_provider_facilities'),
    path('add_facility/', views.add_facility, name='add_facility'),
    path('edit_facility/<int:facility_id>/', views.edit_facility, name='edit_facility'),
    path('delete_facility/<int:facility_id>/', views.delete_facility, name='delete_facility'),
    path('service_provider_bookings/', views.service_provider_bookings, name='service_provider_bookings'),
    path('update_booking_status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('facility_usage_logs/', views.facility_usage_logs, name='facility_usage_logs'),
    path('submit_sp_complaint/', views.submit_sp_complaint, name='submit_sp_complaint'),
    path('view_sp_complaints/', views.view_sp_complaints, name='view_sp_complaints'),
    


    path('medical_store_login/', views.medical_store_login, name='medical_store_login'),
    path('medical_store_home/', views.medical_store_home, name='medical_store_home'),
    path('medical_store_profile/', views.medical_store_profile, name='medical_store_profile'),
    path('medical_store_add_medicines/', views.medical_store_add_medicines, name='medical_store_add_medicines'),
    path('medical_store_view_medicines/', views.medical_store_view_medicines, name='medical_store_view_medicines'),
    path('medical_store_edit_medicine/<int:medicine_id>/', views.medical_store_edit_medicine, name='medical_store_edit_medicine'),
    path('medical_store_delete_medicine/<int:medicine_id>/', views.medical_store_delete_medicine, name='medical_store_delete_medicine'),
    path('medicalstore_dashboard/', views.medicalstore_dashboard, name='medicalstore_dashboard'),
    path('medicalstore_orders/', views.medicalstore_orders, name='medicalstore_orders'),
    path('medicalstore_order_detail/<int:order_id>/', views.medicalstore_order_detail, name='medicalstore_order_detail'),


    path('supermarket_login/', views.supermarket_login, name='supermarket_login'),
    path('supermarket_home/', views.supermarket_home, name='supermarket_home'),
    path('supermarket_profile/', views.supermarket_profile, name='supermarket_profile'),
    path('supermarket_add_category/', views.supermarket_add_category, name='supermarket_add_category'),
    path('supermarket_view_categories/', views.supermarket_view_categories, name='supermarket_view_categories'),
    path('supermarket_edit_category/<int:category_id>/', views.supermarket_edit_category, name='supermarket_edit_category'),
    path('supermarket_delete_category/<int:category_id>/', views.supermarket_delete_category, name='supermarket_delete_category'),
    path('supermarket_add_product/', views.supermarket_add_product, name='supermarket_add_product'),
    path('supermarket_view_products/', views.supermarket_view_products, name='supermarket_view_products'),
    path('supermarket_edit_product/<int:product_id>/', views.supermarket_edit_product, name='supermarket_edit_product'),
    path('supermarket_delete_product/<int:product_id>/', views.supermarket_delete_product, name='supermarket_delete_product'),
    path('supermarket_dashboard/', views.supermarket_dashboard, name='supermarket_dashboard'),
    path('supermarket_orders/', views.supermarket_orders, name='supermarket_orders'),
    path('supermarket_order_detail/<int:order_id>/', views.supermarket_order_detail, name='supermarket_order_detail'),


    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/start/', views.start_chat, name='start_chat'),
    
    
    path('view_notifications/', views.view_notifications, name='view_notifications'),
   

    path('product/<int:item_id>/', views.product_detail, name='product_detail'),
    path('medicine/<int:item_id>/', views.medicine_detail, name='medicine_detail'),
    
    
]