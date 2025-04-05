from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import datetime
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    graduation_year = models.PositiveIntegerField(
        default=datetime.now().year,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.now().year)
        ]
    )
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

class Batch(models.Model):
    graduation_year = models.IntegerField()
    mentors = models.ManyToManyField('BatchMentor', related_name='batches_assigned')

    def __str__(self):
        return f"Batch {self.graduation_year}"

class GraduationYear(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)

class BatchMentor(models.Model):
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='media/mentor_photos/', blank=True, null=True)
    assigned_batches = models.ManyToManyField('GraduationYear', blank=True, related_name='mentors_assigned')
    username = models.CharField(max_length=255, unique=True)

    REQUIRED_FIELDS = ['full_name', 'mobile', 'email']

    def save(self, *args, **kwargs):
        if not self.username:  # Ensure username is set to email if not already set
            self.username = self.email
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name

class Notice(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    media = models.FileField(upload_to='notices/', max_length=255, blank=True, null=True)  # Optional media field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    media = models.FileField(upload_to='events/', max_length=255, blank=True, null=True)  # Make media optional
    date = models.DateField()  # Add event date field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

@receiver(post_save, sender=Alumni)
def populate_graduation_year(sender, instance, **kwargs):
    if instance.graduation_year:  # Ensure graduation_year is not null
        GraduationYear.objects.get_or_create(year=instance.graduation_year)
