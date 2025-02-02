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

class BatchMentorRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = BatchMentor
        fields = ['name', 'email', 'mobile', 'assigned_batches']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password1"]:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()  # Save the many-to-many data for the form
        return user

class BatchMentorLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())