from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser, User
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.conf import settings
import datetime

class Admin(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    class Meta:
        app_label = 'alumni'

class AlumniCoordinator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'alumni'
        db_table = 'alumni_coordinator'  # Ensure the table name is explicitly set

class AlumniManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Alumni(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=255, unique=True, editable=False, primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=255)  # Hashed password
    profile_photo = models.ImageField(upload_to='media/profile_photos/', blank=True, null=True)
    current_job_profile = models.CharField(max_length=255, blank=True, null=True)
    current_company = models.CharField(max_length=255, blank=True, null=True)
    current_job_location = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    sub_district = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    is_international = models.BooleanField(default=False)
    country = models.CharField(max_length=255, blank=True, null=True)
    full_address = models.TextField()
    graduation_year = models.IntegerField()
    experience = models.IntegerField(default=0)
    facebook = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='alumni_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='alumni_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = AlumniManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile', 'city', 'sub_district', 'district', 'state', 'pincode', 'full_address', 'graduation_year', 'experience', 'linkedin']

    def save(self, *args, **kwargs):
        if not self.id:
            last_alumni = Alumni.objects.filter(graduation_year=self.graduation_year).order_by('id').last()
            if last_alumni:
                last_id = int(str(last_alumni.id)[-2:])  # Convert id to string before slicing
                new_id = f"{self.graduation_year}{last_id + 1:02d}"
            else:
                new_id = f"{self.graduation_year}01"
            self.id = new_id
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_active(self):
        return True

class GalleryPhoto(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'alumni'

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class BatchMentorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

    def get_available_mentors(self):
        return self.filter(assigned_batches__isnull=True)

class Batch(models.Model):
    id = models.BigAutoField(primary_key=True)
    graduation_year = models.IntegerField()

    def __str__(self):
        return str(self.graduation_year)

class BatchMentor(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    assigned_batches = models.ManyToManyField(Batch, related_name='mentors')
    username = models.CharField(max_length=255, unique=True, default='')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='batchmentor_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='batchmentor_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile']

    objects = BatchMentorManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'alumni'
        db_table = 'alumni_batchmentor'

class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).total_seconds() < 120  # 2 min expiry