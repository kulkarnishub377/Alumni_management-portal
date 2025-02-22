import sys
import xlwt
from django.http import HttpResponse, JsonResponse
sys.setrecursionlimit(1000)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Admin, Alumni, AlumniCoordinator, Comment, GalleryPhoto
from .forms import (
    AdminRegistrationForm, AlumniRegistrationForm, AlumniCoordinatorRegistrationForm,
    AlumniEditForm, GalleryPhotoForm, CommentForm, AlumniCoordinatorEditForm
)
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path
from django import forms
from . import views
from django.template.loader import render_to_string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now



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
            alumni = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            if password1:
                alumni.set_password(password1)
            alumni.save()
            messages.success(request, 'Profile updated successfully.')
            return render(request, 'alumni/alumni_edit_profile.html', {'form': form, 'success': True})
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
            return redirect('edit_profile')
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
import os
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from .models import Alumni

def share_alumni_profile(request, id):
    try:
        alumni = Alumni.objects.get(pk=id)
        
        # Load header image
        header_image_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'header-2.jpg')

        # Create a blank image
        image = Image.new('RGB', (900, 1300), color=(245, 245, 245))  # Light gray background
        draw = ImageDraw.Draw(image)

        # Load fonts
        font_regular = ImageFont.truetype("arial.ttf", 24)
        font_bold = ImageFont.truetype("arialbd.ttf", 28)
        font_title = ImageFont.truetype("arialbd.ttf", 32)

        # Draw a stylish header
        try:
            header_image = Image.open(header_image_path).resize((900, 180))
            image.paste(header_image, (0, 0))
        except FileNotFoundError:
            draw.rectangle([(0, 0), (900, 180)], fill=(30, 144, 255))  # Blue header fallback
            draw.text((300, 70), "ALUMNI PROFILE", fill="white", font=font_title)

        # Draw a rounded profile picture
        try:
            profile_photo = Image.open(alumni.profile_photo.path).resize((180, 180))
            mask = Image.new('L', (180, 180), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 180, 180), fill=255)

            # Create a circular border
            border = Image.new('RGB', (190, 190), (255, 255, 255))
            border_draw = ImageDraw.Draw(border)
            border_draw.ellipse((0, 0, 190, 190), fill=(255, 255, 255), outline=(0, 0, 0), width=5)

            image.paste(border, (360, 190))
            image.paste(profile_photo, (365, 195), mask)
        except FileNotFoundError:
            draw.text((390, 220), "No Photo", fill="red", font=font_bold)

        # Draw profile details with spacing
        y_offset = 420
        spacing = 40
        text_color = (50, 50, 50)  # Dark gray for readability

        def draw_label(draw, position, label, value):
            draw.text(position, f"{label}:", fill=(30, 144, 255), font=font_bold)  # Blue Labels
            draw.text((position[0] + 200, position[1]), value if value else "N/A", fill=text_color, font=font_regular)

        draw_label(draw, (50, y_offset), "Full Name", alumni.full_name)
        draw_label(draw, (50, y_offset + spacing), "Email", alumni.email)
        draw_label(draw, (50, y_offset + spacing * 2), "Mobile", alumni.mobile)
        draw_label(draw, (50, y_offset + spacing * 3), "Job Profile", alumni.current_job_profile)
        draw_label(draw, (50, y_offset + spacing * 4), "Company", alumni.current_company)
        draw_label(draw, (50, y_offset + spacing * 5), "Location", alumni.current_job_location)
        draw_label(draw, (50, y_offset + spacing * 6), "Sector", alumni.sector)
        draw_label(draw, (50, y_offset + spacing * 7), "City", alumni.city)
        draw_label(draw, (50, y_offset + spacing * 8), "State", alumni.state)
        draw_label(draw, (50, y_offset + spacing * 9), "Graduation Year", str(alumni.graduation_year))
        draw_label(draw, (50, y_offset + spacing * 10), "Experience", str(alumni.experience) + " years")

        # Social Media Links
        social_links = [
            ("LinkedIn", alumni.linkedin),
            ("Facebook", alumni.facebook),
            ("Instagram", alumni.instagram),
            ("GitHub", alumni.github),
        ]

        y_offset += spacing * 11
        for platform, link in social_links:
            if link:
                draw_label(draw, (50, y_offset), platform, link)
                y_offset += spacing

        # Convert to JPEG response
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
    return redirect('alumni_login')

# Register
def register(request):
    return HttpResponse("This is the registration page.")

# Alumni Login
def alumni_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None and isinstance(user, Alumni):
            login(request, user)
            return redirect('alumni_profile')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'alumni/alumni_login.html')
