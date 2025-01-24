from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import django.utils.timezone

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
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('graduation_year', 2000)  # Set a default value for graduation_year
        extra_fields.setdefault('experience', 0)  # Set a default value for experience

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Alumni(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
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
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
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
    REQUIRED_FIELDS = ['username', 'full_name', 'mobile', 'city', 'sub_district', 'district', 'state', 'pincode', 'full_address', 'graduation_year', 'experience', 'linkedin']

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

    class Meta:
        app_label = 'alumni'

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

class BatchMentor(AbstractUser):
    username = None  # Remove the username field
    first_name = None  # Exclude the first_name field
    last_name = None  # Exclude the last_name field
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    assigned_batch = models.CharField(max_length=100)
    date_joined = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='batchmentor_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='batchmentor_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = BatchMentorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile', 'assigned_batch']

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_active(self):
        return True

    class Meta:
        app_label = 'alumni'