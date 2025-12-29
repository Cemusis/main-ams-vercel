from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home & Search
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('view-all/', views.view_all_records, name='view_all_records'),
    
    # Filters (for clickable stats)
    path('filter/available/', views.filter_available, name='filter_available'),
    path('filter/borrowed/', views.filter_borrowed, name='filter_borrowed'),
    path('filter/new-month/', views.filter_new_month, name='filter_new_month'),
    
    # View, Edit, Delete
    path('record/<int:record_id>/', views.view_record, name='view_record'),
    path('record/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('record/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    path('add-record/', views.add_record, name='add_record'),
    path('logs/', views.view_logs, name='view_logs'),
    
    # Borrow/Return - NEW
    path('borrow-return/', views.borrow_return, name='borrow_return'),
    path('borrow/<int:record_id>/', views.borrow_record, name='borrow_record'),
    path('return/<int:transaction_id>/', views.return_record, name='return_record'),
    
    # User Management (Admin only)
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('deactivate-user/<str:email>/', views.deactivate_user, name='deactivate_user'),
    path('activate-user/<str:email>/', views.activate_user, name='activate_user'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    

]

