from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Alumni, Admin, AlumniCoordinator, GalleryPhoto, Comment, BatchMentor, Batch

class AlumniRegistrationForm(UserCreationForm):
    class Meta:
        model = Alumni
        fields = [
            'profile_photo', 'full_name', 'mobile', 'email', 'password1', 'password2', 'current_job_profile',
            'current_company', 'current_job_location', 'city', 'sub_district', 'district',
            'state', 'pincode', 'is_international', 'country', 'full_address', 'graduation_year',
            'experience', 'facebook', 'github', 'instagram', 'linkedin', 'sector'
        ]

class AlumniEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta:
        model = Alumni
        fields = [
            'profile_photo', 'full_name', 'mobile', 'email', 'current_job_profile',
            'current_company', 'current_job_location', 'city', 'sub_district', 'district',
            'state', 'pincode', 'is_international', 'country', 'full_address', 'graduation_year',
            'experience', 'facebook', 'github', 'instagram', 'linkedin', 'sector'
        ]
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'current_job_profile': forms.TextInput(attrs={'class': 'form-control'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'current_job_location': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'sub_district': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'is_international': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'full_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            self.add_error('password2', "Passwords do not match")

        return cleaned_data

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

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class AlumniLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

class BatchMentorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = BatchMentor
        fields = ['email', 'full_name', 'mobile', 'password', 'assigned_batches']
        widgets = {
            'assigned_batches': forms.CheckboxSelectMultiple(),
        }

class BatchMentorLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
