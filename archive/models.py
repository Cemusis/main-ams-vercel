from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, role='Lecturer', **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, role='Admin', **extra_fields)

# User model
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Admin', 'Administrator'),
        ('Secretary', 'Secretary'),
        ('Lecturer', 'Lecturer'),
    ]
    
    email = models.EmailField(unique=True, primary_key=True)
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Lecturer')
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.role})"
    
    class Meta:
        db_table = 'users'


# Physical Location table
class PhysicalLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    shelf_number = models.IntegerField()
    bay_code = models.CharField(max_length=5)
    section_number = models.IntegerField()
    full_location_code = models.CharField(max_length=20, unique=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate full location code (e.g., 5A2)
        self.full_location_code = f"{self.shelf_number}{self.bay_code}{self.section_number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.full_location_code
    
    class Meta:
        db_table = 'physical_location'


# Archive Record table
class ArchiveRecord(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Borrowed', 'Borrowed'),
        ('Archived', 'Archived'),
    ]
    
    SEMESTER_CHOICES = [
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
    ]
    
    EXAM_TYPE_CHOICES = [
        ('Midterm', 'Midterm'),
        ('Final', 'Final'),
        ('Quiz', 'Quiz'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('Exam', 'Exam'),
        ('Internship Report', 'Internship Report'),
        ('Grad Project', 'Graduation Project'),
    ]
    
    record_id = models.AutoField(primary_key=True)
    file_code = models.CharField(max_length=20, unique=True)
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=100)
    lecturer_name = models.CharField(max_length=100)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=10)
    exam_type = models.CharField(max_length=30, choices=EXAM_TYPE_CHOICES, blank=True, null=True)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    cloud_file_id = models.CharField(max_length=255, blank=True, null=True)
    cloud_file_link = models.URLField(blank=True, null=True)
    has_digital_copy = models.BooleanField(default=False)
    physical_location = models.ForeignKey(PhysicalLocation, on_delete=models.PROTECT)
    upload_date = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    def __str__(self):
        return f"{self.file_code} - {self.course_code}"
    
    class Meta:
        db_table = 'archive_record'


# Borrow Transaction table
class BorrowTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    record = models.ForeignKey(ArchiveRecord, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.borrower.email} - {self.record.file_code}"
    
    class Meta:
        db_table = 'borrow_transaction'


# Log table
class Log(models.Model):
    ACTION_CHOICES = [
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete'),
        ('Login', 'Login'),
        ('Logout', 'Logout'),
        ('Borrow', 'Borrow'),
        ('Return', 'Return'),
    ]
    
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    table_affected = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.action_type} by {self.user.email} at {self.timestamp}"
    
    class Meta:
        db_table = 'log'
        ordering = ['-timestamp']