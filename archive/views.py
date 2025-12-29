from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta
import logging
from .forms import LoginForm
from .models import ArchiveRecord, BorrowTransaction, Log, PhysicalLocation
from django.contrib.auth.hashers import make_password
from .models import User



# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            if not form.cleaned_data.get('remember'):
                request.session.set_expiry(1800)
            
            # Log the login
            Log.objects.create(
                user=user,
                action_type='Login',
                table_affected='User',
                details=f'{user.full_name} logged in'
            )
            
            messages.success(request, f'Welcome back, {user.full_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    
    return render(request, 'archive/login.html', {'form': form})

# Logout view
def logout_view(request):
    if request.user.is_authenticated:
        Log.objects.create(
            user=request.user,
            action_type='Logout',
            table_affected='User',
            details=f'{request.user.full_name} logged out'
        )
    
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login')


# Home page with REAL stats
@login_required(login_url='login')
def home(request):
    user = request.user
    context = {'user': user}
    
    # Get REAL statistics from database
    total_records = ArchiveRecord.objects.count()
    available_records = ArchiveRecord.objects.filter(status='Available').count()
    active_borrowings = BorrowTransaction.objects.filter(return_date__isnull=True).count()
    
    # Get LAST 3 activities (not just 1)
    recent_logs = Log.objects.all()[:3]
    recent_activity_list = [log.details for log in recent_logs]
    recent_activity = ' | '.join(recent_activity_list) if recent_activity_list else 'No recent activity'
    
    # Records added this month
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    new_this_month = ArchiveRecord.objects.filter(upload_date__gte=this_month_start).count()
    
    # Different stats based on role
    if user.role == 'Admin':
        context.update({
            'total_records': total_records,
            'available_records': available_records,
            'recent_activity': recent_activity,
        })
    elif user.role == 'Secretary':
        context.update({
            'active_borrowings': active_borrowings,
            'new_this_month': new_this_month,
        })
    else:  # Lecturer
        context.update({
            'total_records': total_records,
        })
    
    return render(request, 'archive/home.html', context)

# Search page
@login_required(login_url='login')
def search(request):
    results = []
    
    if request.GET:
        # Get search parameters
        course_code = request.GET.get('course_code', '')
        course_name = request.GET.get('course_name', '')
        lecturer = request.GET.get('lecturer', '')
        year = request.GET.get('year', '')
        semester = request.GET.get('semester', '')
        doc_type = request.GET.get('doc_type', '')
        
        # Start with all records
        results = ArchiveRecord.objects.all()
        
        # Apply filters
        if course_code:
            results = results.filter(course_code__icontains=course_code)
        if course_name:
            results = results.filter(course_name__icontains=course_name)
        if lecturer:
            results = results.filter(lecturer_name__icontains=lecturer)
        if year:
            results = results.filter(academic_year=year)
        if semester:
            results = results.filter(semester=semester)
        if doc_type:
            results = results.filter(document_type=doc_type)
    
    context = {
        'user': request.user,
        'results': results,
        'searched': bool(request.GET)
    }
    
    return render(request, 'archive/search.html', context)

# View All Records
@login_required(login_url='login')
def view_all_records(request):
    """View all records in the system"""
    records = ArchiveRecord.objects.all().order_by('-upload_date')
    
    context = {
        'user': request.user,
        'records': records,
    }
    
    return render(request, 'archive/view_all_records.html', context)

# View Record Details
@login_required(login_url='login')
def view_record(request, record_id):
    """View full details of a single record"""
    record = ArchiveRecord.objects.get(record_id=record_id)
    
    context = {
        'user': request.user,
        'record': record,
    }
    
    return render(request, 'archive/view_record.html', context)


# Edit Record
@login_required(login_url='login')
def edit_record(request, record_id):
    """Edit existing record (Admin/Secretary only)"""
    
    # Check permission
    if request.user.role not in ['Admin', 'Secretary']:
        messages.error(request, 'You do not have permission to edit records.')
        return redirect('home')
    
    record = ArchiveRecord.objects.get(record_id=record_id)
    
    if request.method == 'POST':
        # Update record with form data
        record.course_code = request.POST.get('course_code')
        record.course_name = request.POST.get('course_name')
        record.lecturer_name = request.POST.get('lecturer_name')
        record.semester = request.POST.get('semester')
        record.academic_year = request.POST.get('academic_year')
        record.exam_type = request.POST.get('exam_type')
        record.document_type = request.POST.get('document_type')
        record.status = request.POST.get('status')
        record.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Update',
            table_affected='ArchiveRecord',
            details=f'Updated record {record.file_code}'
        )
        
        messages.success(request, f'Record {record.file_code} updated successfully!')
        return redirect('view_record', record_id=record.record_id)
    
    context = {
        'user': request.user,
        'record': record,
        'locations': PhysicalLocation.objects.all(),
    }
    
    return render(request, 'archive/edit_record.html', context)


# Delete Record
@login_required(login_url='login')
def delete_record(request, record_id):
    """Delete record (Admin/Secretary only)"""
    
    # Check permission
    if request.user.role not in ['Admin', 'Secretary']:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('home')
    
    record = ArchiveRecord.objects.get(record_id=record_id)
    file_code = record.file_code
    
    # Log the action before deleting
    Log.objects.create(
        user=request.user,
        action_type='Delete',
        table_affected='ArchiveRecord',
        details=f'Deleted record {file_code}'
    )
    
    record.delete()
    
    messages.success(request, f'Record {file_code} deleted successfully!')
    return redirect('search')
# Filter: Available Records
@login_required(login_url='login')
def filter_available(request):
    """Show only available records"""
    records = ArchiveRecord.objects.filter(status='Available').order_by('-upload_date')
    
    context = {
        'user': request.user,
        'records': records,
        'filter_title': 'Available Records',
    }
    
    return render(request, 'archive/filtered_records.html', context)


# Filter: Borrowed Records
@login_required(login_url='login')
def filter_borrowed(request):
    """Show only borrowed records with borrower info"""
    records = ArchiveRecord.objects.filter(status='Borrowed').order_by('-upload_date')
    
    # Get borrower info for each record
    borrowed_info = {}
    for record in records:
        transaction = BorrowTransaction.objects.filter(
            record=record, 
            return_date__isnull=True
        ).first()
        if transaction:
            borrowed_info[record.record_id] = {
                'borrower': transaction.borrower.full_name,
                'date': transaction.borrow_date
            }
    
    context = {
        'user': request.user,
        'records': records,
        'filter_title': 'Active Borrowings',
        'borrowed_info': borrowed_info,
    }
    
    return render(request, 'archive/filtered_records.html', context)


# Filter: New This Month
@login_required(login_url='login')
def filter_new_month(request):
    """Show records added this month"""
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
    records = ArchiveRecord.objects.filter(upload_date__gte=this_month_start).order_by('-upload_date')
    
    context = {
        'user': request.user,
        'records': records,
        'filter_title': 'New This Month',
    }
    
    return render(request, 'archive/filtered_records.html', context)
# Add Record
@login_required(login_url='login')
def add_record(request):
    """Add new archive record (Admin/Secretary only)"""
    
    # Check permission
    if request.user.role not in ['Admin', 'Secretary']:
        messages.error(request, 'You do not have permission to add records.')
        return redirect('home')
    
    if request.method == 'POST':
        # Get form data
        file_code = request.POST.get('file_code')
        course_code = request.POST.get('course_code')
        course_name = request.POST.get('course_name')
        lecturer_name = request.POST.get('lecturer_name')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        exam_type = request.POST.get('exam_type') or None
        document_type = request.POST.get('document_type')
        location_id = request.POST.get('location_id')
        
        # Basic validation
        if not file_code or not course_code or not course_name or not lecturer_name or not semester or not academic_year or not document_type:
            messages.error(request, 'Please fill in all required fields.')
            context = {
                'user': request.user,
                'locations': PhysicalLocation.objects.all(),
            }
            return render(request, 'archive/add_record.html', context)

        # Check if file code already exists
        if ArchiveRecord.objects.filter(file_code=file_code).exists():
            messages.error(request, f'File code {file_code} already exists!')
            context = {
                'user': request.user,
                'locations': PhysicalLocation.objects.all(),
            }
            return render(request, 'archive/add_record.html', context)

        # Validate location
        try:
            location = PhysicalLocation.objects.get(location_id=location_id)
        except (PhysicalLocation.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Invalid physical location selected.')
            context = {
                'user': request.user,
                'locations': PhysicalLocation.objects.all(),
            }
            return render(request, 'archive/add_record.html', context)

        # Create record (catch DB integrity errors to show helpful message)
        try:
            record = ArchiveRecord.objects.create(
                file_code=file_code,
                course_code=course_code,
                course_name=course_name,
                lecturer_name=lecturer_name,
                semester=semester,
                academic_year=academic_year,
                exam_type=exam_type,
                document_type=document_type,
                physical_location=location,
                uploaded_by=request.user,
                status='Available'
            )
        except IntegrityError as e:
            logger = logging.getLogger(__name__)
            logger.exception('IntegrityError creating ArchiveRecord: %s', e)
            # Show concise message to the user; detailed info is in server logs
            messages.error(request, f'Could not create record: database integrity error ({e.__class__.__name__}).')
            context = {
                'user': request.user,
                'locations': PhysicalLocation.objects.all(),
            }
            return render(request, 'archive/add_record.html', context)
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Create',
            table_affected='ArchiveRecord',
            details=f'Created new record {file_code}'
        )
        
        messages.success(request, f'Record {file_code} created successfully!')
        return redirect('view_record', record_id=record.record_id)
    
    context = {
        'user': request.user,
        'locations': PhysicalLocation.objects.all(),
    }
    
    return render(request, 'archive/add_record.html', context)
# Borrow/Return Management
@login_required(login_url='login')
def borrow_return(request):
    """Borrow and return management page"""
    
    # Get all available records for borrowing
    available_records = ArchiveRecord.objects.filter(status='Available').order_by('course_code')
    
    # Get active borrowings based on role
    if request.user.role in ['Admin', 'Secretary']:
        # Admin/Secretary see ALL borrowings
        active_borrowings = BorrowTransaction.objects.filter(
            return_date__isnull=True
        ).select_related('record', 'borrower').order_by('-borrow_date')
    else:
        # Lecturers see ONLY their own borrowings
        active_borrowings = BorrowTransaction.objects.filter(
            return_date__isnull=True,
            borrower=request.user
        ).select_related('record', 'borrower').order_by('-borrow_date')
    
    context = {
        'user': request.user,
        'available_records': available_records,
        'active_borrowings': active_borrowings,
    }
    
    return render(request, 'archive/borrow_return.html', context)

# Borrow a Record
@login_required(login_url='login')
def borrow_record(request, record_id):
    """Borrow a record"""
    
    if request.method == 'POST':
        record = ArchiveRecord.objects.get(record_id=record_id)
        
        # Check if already borrowed
        if record.status == 'Borrowed':
            messages.error(request, f'{record.file_code} is already borrowed!')
            return redirect('borrow_return')
        
        # Create borrow transaction
        BorrowTransaction.objects.create(
            record=record,
            borrower=request.user,
            borrow_date=timezone.now()
        )
        
        # Update record status
        record.status = 'Borrowed'
        record.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Borrow',
            table_affected='ArchiveRecord',
            details=f'{request.user.full_name} borrowed {record.file_code}'
        )
        
        messages.success(request, f'Successfully borrowed {record.file_code}!')
        return redirect('borrow_return')
    
    return redirect('borrow_return')


# Return a Record
@login_required(login_url='login')
def return_record(request, transaction_id):
    """Return a borrowed record"""
    
    if request.method == 'POST':
        transaction = BorrowTransaction.objects.get(transaction_id=transaction_id)
        record = transaction.record
        
        # Check permission (Admin/Secretary or the borrower themselves)
        if request.user.role not in ['Admin', 'Secretary'] and transaction.borrower != request.user:
            messages.error(request, 'You do not have permission to return this record.')
            return redirect('borrow_return')
        
        # Update transaction
        transaction.return_date = timezone.now()
        transaction.save()
        
        # Update record status
        record.status = 'Available'
        record.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Return',
            table_affected='ArchiveRecord',
            details=f'{transaction.borrower.full_name} returned {record.file_code}'
        )
        
        messages.success(request, f'Successfully returned {record.file_code}!')
        return redirect('borrow_return')
    
    return redirect('borrow_return')

# View Activity Logs
@login_required(login_url='login')
def view_logs(request):
    """View all activity logs (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to view logs.')
        return redirect('home')
    
    # Get logs from last month
    one_month_ago = timezone.now() - timedelta(days=30)
    logs = Log.objects.filter(timestamp__gte=one_month_ago).order_by('-timestamp')
    
    context = {
        'user': request.user,
        'logs': logs,
    }
    
    return render(request, 'archive/view_logs.html', context)

@login_required(login_url='login')
def manage_users(request):
    """User management page (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('home')
    
    users = User.objects.all().order_by('-created_at')
    
    context = {
        'user': request.user,
        'users': users,
    }
    
    return render(request, 'archive/manage_users.html', context)


@login_required(login_url='login')
def add_user(request):
    """Add new user (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to add users.')
        return redirect('home')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('manage_users')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
            return redirect('manage_users')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, f'User with email {email} already exists!')
            return redirect('manage_users')
        
        # Create user
        user = User.objects.create(
            email=email,
            full_name=full_name,
            role=role,
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Create',
            table_affected='User',
            details=f'Created new user: {full_name} ({email}) - {role}'
        )
        
        messages.success(request, f'User {full_name} created successfully!')
        return redirect('manage_users')
    
    return redirect('manage_users')


@login_required(login_url='login')
def deactivate_user(request, email):
    """Deactivate user (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to deactivate users.')
        return redirect('home')
    
    if request.method == 'POST':
        target_user = User.objects.get(email=email)
        
        # Don't allow deactivating yourself
        if target_user.email == request.user.email:
            messages.error(request, 'You cannot deactivate your own account!')
            return redirect('manage_users')
        
        target_user.is_active = False
        target_user.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Update',
            table_affected='User',
            details=f'Deactivated user: {target_user.full_name} ({email})'
        )
        
        messages.success(request, f'User {target_user.full_name} deactivated!')
        return redirect('manage_users')
    
    return redirect('manage_users')


@login_required(login_url='login')
def activate_user(request, email):
    """Activate user (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to activate users.')
        return redirect('home')
    
    if request.method == 'POST':
        target_user = User.objects.get(email=email)
        target_user.is_active = True
        target_user.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Update',
            table_affected='User',
            details=f'Activated user: {target_user.full_name} ({email})'
        )
        
        messages.success(request, f'User {target_user.full_name} activated!')
        return redirect('manage_users')
    
    return redirect('manage_users')


@login_required(login_url='login')
def reset_password(request, email):
    """Reset user password to default (Admin only)"""
    
    # Check permission
    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to reset passwords.')
        return redirect('home')
    
    if request.method == 'POST':
        target_user = User.objects.get(email=email)
        
        # Reset to default password
        default_password = 'password123'
        target_user.set_password(default_password)
        target_user.save()
        
        # Log the action
        Log.objects.create(
            user=request.user,
            action_type='Update',
            table_affected='User',
            details=f'Reset password for user: {target_user.full_name} ({email})'
        )
        
        messages.success(request, f'Password reset for {target_user.full_name}! New password: {default_password}')
        return redirect('manage_users')
    
    return redirect('manage_users')