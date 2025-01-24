from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Alumni, Admin, AlumniCoordinator, GalleryPhoto, Comment, BatchMentor

class AlumniRegistrationForm(UserCreationForm):
    class Meta:
        model = Alumni
        fields = [
            'profile_photo', 'full_name', 'mobile', 'email', 'password1', 'password2', 'current_job_profile',
            'current_company', 'current_job_location', 'city', 'sub_district', 'district',
            'state', 'pincode', 'is_international', 'country', 'full_address', 'graduation_year',
            'experience', 'facebook', 'github', 'instagram', 'linkedin', 'sector'
        ]

class AlumniEditForm(UserChangeForm):
    class Meta:
        model = Alumni
        fields = [
            'profile_photo', 'full_name', 'mobile', 'email', 'current_job_profile',
            'current_company', 'current_job_location', 'city', 'sub_district', 'district',
            'state', 'pincode', 'is_international', 'country', 'full_address', 'graduation_year',
            'experience', 'facebook', 'github', 'instagram', 'linkedin', 'sector'
        ]

class AlumniLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class AdminRegistrationForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['name', 'mobile', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class AlumniCoordinatorRegistrationForm(forms.ModelForm):
    class Meta:
        model = AlumniCoordinator
        fields = ['name', 'email', 'password', 'mobile']
        widgets = {
            'password': forms.PasswordInput(),
        }

class AlumniCoordinatorLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class AlumniCoordinatorEditForm(forms.ModelForm):
    class Meta:
        model = AlumniCoordinator
        fields = ['name', 'email', 'mobile']

class GalleryPhotoForm(forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = ['title', 'image', 'description']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class BatchMentorRegistrationForm(UserCreationForm):
    class Meta:
        model = BatchMentor
        fields = ['name', 'email', 'mobile', 'password1', 'password2', 'assigned_batch', 'date_joined']

class BatchMentorLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())