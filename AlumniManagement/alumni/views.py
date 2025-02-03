import sys
import csv
import xlwt
from django.http import HttpResponse, JsonResponse
sys.setrecursionlimit(1000)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Admin, Alumni, AlumniCoordinator, Comment, GalleryPhoto, BatchMentor, Batch  # Add Batch
from .forms import (
    AdminRegistrationForm, AlumniRegistrationForm, AlumniCoordinatorRegistrationForm,
    AlumniEditForm, GalleryPhotoForm, CommentForm, AlumniCoordinatorEditForm, BatchMentorRegistrationForm, BatchMentorLoginForm, BatchMentorForm, AlumniLoginForm
)
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path
from django import forms
from . import views
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import json
from django.contrib.auth.tokens import default_token_generator

# Home Page
def home(request):
    return render(request, 'home.html')

# Admin Login
def admin_login(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            admin = Admin.objects.get(email=email, password=password)
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            return render(request, 'alumni/templates/admin/admin_login.html', {'error': 'Invalid credentials'})
    return render(request, 'alumni/templates/admin/admin_login.html')

# Admin Registration
def admin_registration(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_login')
    else:
        form = AdminRegistrationForm()
    return render(request, 'alumni/templates/admin/admin_registration.html', {'form': form})

# Admin Dashboard
def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    alumni_list = Alumni.objects.all()
    return render(request, 'alumni/templates/admin/admin_dashboard.html', {'alumni_list': alumni_list})

# Alumni Coordinator Login
def alumni_coordinator_login(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            coordinator = AlumniCoordinator.objects.get(email=email, password=password)
            request.session['coordinator_id'] = coordinator.id
            return redirect('alumni_coordinator_dashboard')
        except AlumniCoordinator.DoesNotExist:
            return render(request, 'alumni_coordinator/alumni_coordinator_login.html', {'error': 'Invalid credentials'})
    return render(request, 'alumni_coordinator/alumni_coordinator_login.html')

# Alumni Coordinator Registration
def alumni_coordinator_registration(request):
    if request.method == 'POST':
        form = AlumniCoordinatorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('alumni_coordinator_login')
    else:
        form = AlumniCoordinatorRegistrationForm()
    return render(request, 'alumni_coordinator/alumni_coordinator_registration.html', {'form': form})

# Alumni Coordinator Dashboard
def alumni_coordinator_dashboard(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    coordinator = AlumniCoordinator.objects.get(pk=request.session['coordinator_id'])
    alumni_list = Alumni.objects.all()
    return render(request, 'alumni_coordinator/alumni_coordinator_dashboard.html', {
        'coordinator': coordinator,
        'alumni_list': alumni_list
    })

# Alumni Coordinator Edit Profile
def edit_coordinator_profile(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    coordinator = AlumniCoordinator.objects.get(pk=request.session['coordinator_id'])
    if request.method == 'POST':
        form = AlumniCoordinatorRegistrationForm(request.POST, instance=coordinator)
        if form.is_valid():
            form.save()
            return redirect('alumni_coordinator_dashboard')
    else:
        form = AlumniCoordinatorRegistrationForm(instance=coordinator)
    return render(request, 'alumni_coordinator/edit_coordinator_profile.html', {'form': form})

def edit_alumni_coordinator_profile(request):
    if request.method == 'POST':
        form = AlumniCoordinatorEditForm(request.POST, instance=request.user.alumnicoordinator)
        if form.is_valid():
            form.save()
            return redirect('alumni_coordinator_profile')
    else:
        form = AlumniCoordinatorEditForm(instance=request.user.alumnicoordinator)
    return render(request, 'alumni/edit_alumni_coordinator_profile.html', {'form': form})

# Alumni Registration
def alumni_registration(request):
    if request.method == 'POST':
        form = AlumniRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                alumni = form.save(commit=False)
                if 'is_international' not in request.POST:
                    alumni.is_international = False
                alumni.save()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('alumni_login')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AlumniRegistrationForm(initial={'is_international': False})
    return render(request, 'alumni/alumni_registration.html', {'form': form})

# Alumni Login
def alumni_login(request):
    if request.method == 'POST':
        form = AlumniLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and isinstance(user, Alumni):
                login(request, user)
                return redirect('alumni_profile')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AlumniLoginForm()
    return render(request, 'alumni/alumni_login.html', {'form': form})

# Alumni Profile
def alumni_profile(request):
    if not request.user.is_authenticated:
        return redirect('alumni_login')
    try:
        alumni = Alumni.objects.get(email=request.user.email)
    except Alumni.DoesNotExist:
        messages.error(request, 'Alumni profile not found.')
        return redirect('alumni_login')
    return render(request, 'alumni/alumni_profile.html', {'alumni': alumni})

# Alumni Edit Profile
def alumni_edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('alumni_login')
    alumni = Alumni.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = AlumniEditForm(request.POST, request.FILES, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('alumni_edit_profile')  # Redirect to the same page
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AlumniEditForm(instance=alumni)
    return render(request, 'alumni/alumni_edit_profile.html', {'form': form})

# Edit Alumni
def edit_alumni(request, id):
    alumni = Alumni.objects.get(pk=id)
    if request.method == 'POST':
        form = AlumniEditForm(request.POST, request.FILES, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('alumni_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AlumniEditForm(instance=alumni)
    return render(request, 'alumni/alumni_edit_profile.html', {'form': form})

# Edit Alumni Profile
def edit_profile(request):
    if request.method == 'POST':
        form = AlumniEditForm(request.POST, request.FILES, instance=request.user.alumni_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('edit_profile')  # Redirect to the same page
    else:
        form = AlumniEditForm(instance=request.user.alumni_profile)
    
    return render(request, 'alumni/alumni_edit_profile.html', {'form': form})

# Delete Alumni
def delete_alumni(request, id):
    alumni = Alumni.objects.get(pk=id)
    alumni.delete()
    return redirect('alumni_coordinator_dashboard')

# Export Alumni Data to Excel
def export_alumni_to_excel(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="alumni_data.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Alumni Data')

    # Define the columns
    columns = [
        'Full Name', 'Email', 'Mobile', 'Profile Photo', 'Current Job Profile', 'Current Company',
        'Current Job Location', 'City', 'Sub District', 'District', 'State', 'Pincode',
        'Is International', 'Country', 'Full Address', 'Graduation Year', 'Experience', 'Facebook',
        'GitHub', 'Instagram', 'LinkedIn', 'Sector'
    ]

    # Write the column headers
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Write the data rows
    rows = Alumni.objects.all().values_list(
        'full_name', 'email', 'mobile', 'profile_photo', 'current_job_profile', 'current_company',
        'current_job_location', 'city', 'sub_district', 'district', 'state', 'pincode',
        'is_international', 'country', 'full_address', 'graduation_year', 'experience', 'facebook',
        'github', 'instagram', 'linkedin', 'sector'
    )

    for row_num, row in enumerate(rows, start=1):
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))

    wb.save(response)
    return response

def new_func():
    header_style = xlwt.easyxf('font: bold 1')

# Share Alumni Profile
def share_alumni_profile(request, id):
    try:
        alumni = Alumni.objects.get(pk=id)
        header_image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'header-2.jpg')
        
        # Create a blank image
        image = Image.new('RGB', (800, 1200), color='white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 20)
        font_bold = ImageFont.truetype("arialbd.ttf", 24)

        # Draw the header image
        try:
            header_image = Image.open(header_image_path)
            header_image = header_image.resize((800, 200))
            image.paste(header_image, (0, 0))
        except FileNotFoundError:
            draw.text((20, 20), "Header Image Not Found", fill="red", font=font_bold)

        # Draw the profile photo
        try:
            profile_photo = Image.open(alumni.profile_photo.path)
            profile_photo = profile_photo.resize((150, 150))
            image.paste(profile_photo, (325, 220))
        except FileNotFoundError:
            draw.text((325, 220), "Profile Photo Not Found", fill="red", font=font_bold)

        # Draw the profile details
        def draw_text(draw, position, label, value, font, label_font):
            if value:
                draw.text(position, f"{label}: {value}", fill="black", font=font)
            else:
                draw.text(position, f"{label}: N/A", fill="black", font=font)

        draw_text(draw, (20, 400), "• Full Name", alumni.full_name, font, font_bold)
        draw_text(draw, (20, 440), "• Email", alumni.email, font, font_bold)
        draw_text(draw, (20, 480), "• Mobile", alumni.mobile, font, font_bold)
        draw_text(draw, (20, 520), "• Current Job Profile", alumni.current_job_profile, font, font_bold)
        draw_text(draw, (20, 560), "• Current Company", alumni.current_company, font, font_bold)
        draw_text(draw, (20, 600), "• Current Job Location", alumni.current_job_location, font, font_bold)
        draw_text(draw, (20, 640), "• Sector", alumni.sector, font, font_bold)
        draw_text(draw, (20, 680), "• City", alumni.city, font, font_bold)
        draw_text(draw, (20, 720), "• Sub District", alumni.sub_district, font, font_bold)
        draw_text(draw, (20, 760), "• District", alumni.district, font, font_bold)
        draw_text(draw, (20, 800), "• State", alumni.state, font, font_bold)
        draw_text(draw, (20, 840), "• Pincode", alumni.pincode, font, font_bold)
        draw_text(draw, (20, 880), "• Country", alumni.country, font, font_bold)
        draw_text(draw, (20, 920), "• Full Address", alumni.full_address, font, font_bold)
        draw_text(draw, (20, 960), "• Graduation Year", alumni.graduation_year, font, font_bold)
        draw_text(draw, (20, 1000), "• Experience", alumni.experience, font, font_bold)
        draw_text(draw, (20, 1040), "• LinkedIn", alumni.linkedin, font, font_bold)
        draw_text(draw, (20, 1080), "• Facebook", alumni.facebook, font, font_bold)
        draw_text(draw, (20, 1120), "• Instagram", alumni.instagram, font, font_bold)
        draw_text(draw, (20, 1160), "• GitHub", alumni.github, font, font_bold)

        response = HttpResponse(content_type="image/jpeg")
        image.save(response, "JPEG")
        return response
    except Alumni.DoesNotExist:
        return HttpResponse("Alumni not found", status=404)

# Gallery Page
def gallery(request):
    photos = GalleryPhoto.objects.all()
    return render(request, 'gallery.html', {'photos': photos})

# About Us Page
def about_us(request):
    return render(request, 'about_us.html')

# Manage Gallery Photos (Admin)
def manage_gallery_photos_admin(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    photos = GalleryPhoto.objects.all()
    return render(request, 'admin/manage_gallery_photos.html', {'photos': photos})

# Manage Gallery Photos (AlumniCoordinator)
def manage_gallery_photos_coordinator(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    photos = GalleryPhoto.objects.all()
    return render(request, 'alumni_coordinator/manage_gallery_photos.html', {'photos': photos})

# Add Gallery Photo
def add_gallery_photo(request):
    if request.method == 'POST':
        form = GalleryPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_gallery_photos_admin' if 'admin_id' in request.session else 'manage_gallery_photos_coordinator')
    else:
        form = GalleryPhotoForm()
    return render(request, 'alumni_coordinator/add_gallery_photo.html', {'form': form})

# Delete Gallery Photo
def delete_gallery_photo(request, id):
    photo = GalleryPhoto.objects.get(pk=id)
    photo.delete()
    return redirect('manage_gallery_photos_admin' if 'admin_id' in request.session else 'manage_gallery_photos_coordinator')

# Manage Comments (Admin)
def manage_comments_admin(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    comments = Comment.objects.all()
    return render(request, 'admin/manage_comments.html', {'comments': comments})

# Manage Comments (AlumniCoordinator)
def manage_comments_coordinator(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    comments = Comment.objects.all()
    return render(request, 'alumni_coordinator/manage_comments.html', {'comments': comments})

# Add Comment
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_comments_admin' if 'admin_id' in request.session else 'manage_comments_coordinator')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

# Delete Comment
def delete_comment(request, id):
    comment = Comment.objects.get(pk=id)
    comment.delete()
    return redirect('manage_comments_admin' if 'admin_id' in request.session else 'manage_comments_coordinator')

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# Register
def register(request):
    return HttpResponse("This is the registration page.")

# Batch Mentor Registration
def batch_mentor_registration(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    if request.method == 'POST':
        form = BatchMentorRegistrationForm(request.POST)
        if form.is_valid():
            mentor = form.save(commit=False)
            mentor.set_password(form.cleaned_data['password1'])
            mentor.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('batch_mentor_login')
    else:
        form = BatchMentorRegistrationForm()
    return render(request, 'alumni_coordinator/batch_mentor_registration.html', {'form': form})

# Batch Mentor Login
def batch_mentor_login(request):
    if request.method == 'POST':
        form = BatchMentorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and isinstance(user, BatchMentor):
                login(request, user)
                request.session['mentor_id'] = user.id  # Set the session variable
                return redirect('batch_mentor_dashboard')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Invalid email or password')
    else:
        form = BatchMentorLoginForm()
    return render(request, 'alumni_coordinator/batch_mentor_login.html', {'form': form})

# Batch Mentor Dashboard
def batch_mentor_dashboard(request):
    if 'mentor_id' not in request.session:
        return redirect('batch_mentor_login')
    mentor = BatchMentor.objects.get(pk=request.session['mentor_id'])
    assigned_batches = mentor.assigned_batches.all()
    alumni_list = Alumni.objects.filter(graduation_year__in=assigned_batches.values_list('graduation_year', flat=True))
    return render(request, 'batch_mentor/batch_mentor_dashboard.html', {
        'mentor': mentor,
        'alumni_list': alumni_list,
        'assigned_batches': assigned_batches
    })

# View Batch Mentors
def view_batch_mentors(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    mentors = BatchMentor.objects.all()
    return render(request, 'alumni_coordinator/view_batch_mentors.html', {'mentors': mentors})

# Edit Batch Mentor
def edit_batch_mentor(request, id):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    mentor = get_object_or_404(BatchMentor, pk=id)
    if request.method == 'POST':
        form = BatchMentorForm(request.POST, instance=mentor)
        if form.is_valid():
            form.save()
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, 'Batch Mentor updated successfully.')
            return redirect('view_batch_mentors')
    else:
        form = BatchMentorForm(instance=mentor)
    batches = Batch.objects.all()
    return render(request, 'alumni_coordinator/edit_batch_mentor.html', {'form': form, 'mentor': mentor, 'batches': batches})

def view_alumni_in_batches(request, mentor_id):
    mentor = get_object_or_404(BatchMentor, pk=mentor_id)
    assigned_batches = mentor.assigned_batches.all()
    alumni_list = Alumni.objects.filter(graduation_year__in=assigned_batches.values_list('graduation_year', flat=True))
    return render(request, 'view_alumni_in_batches.html', {
        'mentor': mentor,
        'alumni_list': alumni_list,
        'assigned_batches': assigned_batches
    })

# Delete Batch Mentor
def delete_batch_mentor(request, id):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')
    mentor = get_object_or_404(BatchMentor, pk=id)
    mentor.delete()
    messages.success(request, 'Batch Mentor deleted successfully.')
    return redirect('view_batch_mentors')


def edit_batch_mentor(request, id):

    mentor = get_object_or_404(BatchMentor, id=id)

    form = BatchMentorForm(request.POST or None, instance=mentor)

    if form.is_valid():

        form.save()

        return redirect('view_batch_mentors')

    batches = Batch.objects.all()

    return render(request, 'alumni_coordinator/edit_batch_mentor.html', {'form': form, 'batches': batches, 'mentor': mentor})


# Export Batch Mentor Data to Excel
def export_batch_mentor_to_excel(request):
    if 'mentor_id' not in request.session:
        return redirect('batch_mentor_login')
    
    mentor = BatchMentor.objects.get(pk=request.session['mentor_id'])
    alumni_list = Alumni.objects.filter(graduation_year__in=mentor.assigned_batches.values_list('graduation_year', flat=True))
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="alumni_data_batch_{mentor.id}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Alumni Data')

    # Define the columns
    columns = [
        'Full Name', 'Email', 'Mobile', 'Profile Photo', 'Current Job Profile', 'Current Company',
        'Current Job Location', 'City', 'Sub District', 'District', 'State', 'Pincode',
        'Is International', 'Country', 'Full Address', 'Graduation Year', 'Experience', 'Facebook',
        'GitHub', 'Instagram', 'LinkedIn', 'Sector'
    ]

    # Write the column headers
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Write the data rows
    rows = alumni_list.values_list(
        'full_name', 'email', 'mobile', 'profile_photo', 'current_job_profile', 'current_company',
        'current_job_location', 'city', 'sub_district', 'district', 'state', 'pincode',
        'is_international', 'country', 'full_address', 'graduation_year', 'experience', 'facebook',
        'github', 'instagram', 'linkedin', 'sector'
    )

    for row_num, row in enumerate(rows, start=1):
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))

    wb.save(response)
    return response

def assign_batch_to_mentor(request):
    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        batch_id = request.POST.get('batch_id')
        mentor = BatchMentor.objects.get(id=mentor_id)
        batch = Batch.objects.get(id=batch_id)
        mentor.assigned_batches.add(batch)
        return redirect('view_batch_mentors')
    mentors = BatchMentor.objects.all()
    batches = Batch.objects.all()
    return render(request, 'assign_batch.html', {'mentors': mentors, 'batches': batches})

def view_alumni_in_batches(request, mentor_id):
    mentor = get_object_or_404(BatchMentor, pk=mentor_id)
    assigned_batches = mentor.assigned_batches.all()
    alumni_list = Alumni.objects.filter(graduation_year__in=assigned_batches.values_list('graduation_year', flat=True))
    return render(request, 'view_alumni_in_batches.html', {
        'mentor': mentor,
        'alumni_list': alumni_list,
        'assigned_batches': assigned_batches
    })

from django.shortcuts import render, get_object_or_404
from .models import BatchMentor, Alumni

def view_available_batch_mentors(request):
    available_mentors = BatchMentor.objects.get_available_mentors()
    return render(request, 'batch_mentor/view_available_batch_mentors.html', {'available_mentors': available_mentors})

def view_alumni_in_batches(request, mentor_id):
    mentor = get_object_or_404(BatchMentor, id=mentor_id)
    assigned_batches = mentor.assigned_batches.all()
    alumni_list = Alumni.objects.filter(graduation_year__in=[batch.graduation_year for batch in assigned_batches])
    return render(request, 'batch_mentor/view_alumni_in_batches.html', {'mentor': mentor, 'assigned_batches': assigned_batches, 'alumni_list': alumni_list})

def edit_batch_mentor(request, id):
    mentor = get_object_or_404(BatchMentor, id=id)
    if request.method == 'POST':
        form = BatchMentorForm(request.POST, instance=mentor)
        if form.is_valid():
            form.save()
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, 'Batch Mentor updated successfully.')
            return redirect('view_batch_mentors')
    else:
        form = BatchMentorForm(instance=mentor)
    return render(request, 'alumni_coordinator/edit_batch_mentor.html', {'form': form, 'mentor': mentor})

def delete_batch_mentor(request, id):
    mentor = get_object_or_404(BatchMentor, id=id)
    if request.method == 'POST':
        mentor.delete()
        messages.success(request, 'Batch Mentor deleted successfully.')
        return redirect('view_batch_mentors')
    return render(request, 'alumni_coordinator/delete_batch_mentor.html', {'mentor': mentor})

def alumni_forgot_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        mobile = data.get('mobile')
        try:
            alumni = Alumni.objects.get(email=email, mobile=mobile)
            return JsonResponse({'success': True})
        except Alumni.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid email or mobile number.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def alumni_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('alumni_login')
        try:
            alumni = Alumni.objects.get(email=email)
            alumni.set_password(password1)
            alumni.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('alumni_login')
        except Alumni.DoesNotExist:
            messages.error(request, 'Invalid email.')
    return redirect('alumni_login')
