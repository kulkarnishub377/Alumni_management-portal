import sys
import csv
import xlwt
from django.http import HttpResponse
sys.setrecursionlimit(1000)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Admin, Alumni, AlumniCoordinator, Comment
from .models import GalleryPhoto  # Uncomment this line to use GalleryPhoto
from .forms import AdminRegistrationForm, AlumniRegistrationForm, AlumniCoordinatorRegistrationForm, AlumniEditForm, GalleryPhotoForm, CommentForm
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path
from . import views
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
from .forms import AlumniCoordinatorEditForm

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
            form.save()
            return redirect('alumni_login')
    else:
        form = AlumniRegistrationForm()
    return render(request, 'alumni/alumni_registration.html', {'form': form, 'form_action': 'alumni_registration'})

# Alumni Login
def alumni_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                request.session['alumni_id'] = user.id  # Update session with alumni ID
                return redirect('alumni_profile')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Invalid email or password')
    else:
        form = AuthenticationForm()
    return render(request, 'alumni/alumni_login.html', {'form': form})

# Alumni Profile
def alumni_profile(request):
    if not request.user.is_authenticated:
        return redirect('alumni_login')
    alumni = Alumni.objects.get(email=request.user.email)
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
            # Update session data
            request.session['alumni_id'] = alumni.id
            messages.success(request, 'Profile updated successfully.')
            return redirect('alumni_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AlumniEditForm(instance=alumni)
    return render(request, 'alumni/alumni_edit_profile.html', {'form': form})

# Edit Alumni
def edit_alumni(request, id):
    alumni = Alumni.objects.get(pk=id)
    if request.method == 'POST':
        form = AlumniRegistrationForm(request.POST, request.FILES, instance=alumni)
        if form.is_valid():
            form.save()
            return redirect('alumni_profile')
    else:
        form = AlumniRegistrationForm(instance=alumni)
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
        'Profile Photo', 'Name', 'Email', 'Mobile', 'Current Job Profile', 'Current Company',
        'Current Job Location', 'City', 'Sub District', 'District', 'State', 'Pincode',
        'Country', 'Graduation Year', 'Experience', 'LinkedIn', 'Facebook', 'Instagram', 'GitHub'
    ]

    # Write the column headers
    for col_num, column_title in enumerate(columns):
        ws.write(0, col_num, column_title)

    # Write the data rows
    rows = Alumni.objects.all().values_list(
        'profile_photo', 'name', 'email', 'mobile', 'current_job_profile', 'current_company',
        'current_job_location', 'city', 'sub_district', 'district', 'state', 'pincode',
        'country', 'graduation_year', 'experience', 'linkedin', 'facebook', 'instagram', 'github'
    )

    for row_num, row in enumerate(rows, start=1):
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))

    wb.save(response)
    return response

# Share Alumni Profile
def share_alumni_profile(request, id):
    if not request.user.is_authenticated:
        return redirect('alumni_login')
    alumni = Alumni.objects.get(pk=id)
    
    # Generate profile card image
    card = Image.new('RGB', (600, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(card)
    
    # Use a regular available font
    font_bold = ImageFont.load_default()
    font_regular = ImageFont.load_default()

    # Add college and department name
    draw.text((20, 20), "Dr. Vithalrao Vikhe Patil College of Engineering", fill="blue", font=font_bold)
    draw.text((20, 50), "Department of Electronics and Telecommunication", fill="blue", font=font_bold)

    # Add profile photo
    if alumni.profile_photo:
        profile_photo = Image.open(alumni.profile_photo.path)
        profile_photo = profile_photo.resize((100, 100))
        card.paste(profile_photo, (20, 100))
        # Add text details with bold labels and bullet points
        draw.text((140, 100), "• Name:", fill="black", font=font_bold)
        draw.text((240, 100), alumni.name, fill="black", font=font_regular)
        
        draw.text((140, 130), "• Email:", fill="black", font=font_bold)
        draw.text((240, 130), alumni.email, fill="black", font=font_regular)
        
        draw.text((140, 160), "• Mobile:", fill="black", font=font_bold)
        draw.text((240, 160), alumni.mobile, fill="black", font=font_regular)
        
        draw.text((140, 190), "• Job:", fill="black", font=font_bold)
        draw.text((240, 190), alumni.current_job_profile, fill="black", font=font_regular)
        
        draw.text((140, 220), "• Company:", fill="black", font=font_bold)
        draw.text((240, 220), alumni.current_company, fill="black", font=font_regular)
        
        draw.text((140, 250), "• Location:", fill="black", font=font_bold)
        draw.text((240, 250), alumni.current_job_location, fill="black", font=font_regular)
        
        draw.text((140, 280), "• City:", fill="black", font=font_bold)
        draw.text((240, 280), alumni.city, fill="black", font=font_regular)
        
        draw.text((140, 310), "• Sub District:", fill="black", font=font_bold)
        draw.text((240, 310), alumni.sub_district, fill="black", font=font_regular)
        
        draw.text((140, 340), "• District:", fill="black", font=font_bold)
        draw.text((240, 340), alumni.district, fill="black", font=font_regular)
        
        draw.text((140, 370), "• State:", fill="black", font=font_bold)
        draw.text((240, 370), alumni.state, fill="black", font=font_regular)
        
        draw.text((140, 400), "• Pincode:", fill="black", font=font_bold)
        draw.text((240, 400), alumni.pincode, fill="black", font=font_regular)
        
        draw.text((140, 430), "• Country:", fill="black", font=font_bold)
        draw.text((240, 430), alumni.country, fill="black", font=font_regular)
        
        draw.text((140, 460), "• Full Address:", fill="black", font=font_bold)
        draw.text((240, 460), alumni.full_address, fill="black", font=font_regular)
        
        draw.text((140, 490), "• Graduation Year:", fill="black", font=font_bold)
        draw.text((280, 490), str(alumni.graduation_year), fill="black", font=font_regular)
        
        draw.text((140, 520), "• Experience:", fill="black", font=font_bold)
        draw.text((240, 520), f"{alumni.experience} years", fill="black", font=font_regular)
        
        draw.text((140, 550), "• LinkedIn:", fill="black", font=font_bold)
        draw.text((220, 550), alumni.linkedin, fill="black", font=font_regular)
        
        draw.text((140, 580), "• Facebook:", fill="black", font=font_bold)
        draw.text((220, 580), alumni.facebook, fill="black", font=font_regular)
        
        draw.text((140, 610), "• Instagram:", fill="black", font=font_bold)
        draw.text((220, 610), alumni.instagram, fill="black", font=font_regular)
        
        draw.text((140, 640), "• GitHub:", fill="black", font=font_bold)
        draw.text((200, 640), alumni.github, fill="black", font=font_regular)

    # Save image to a BytesIO object
    image_io = BytesIO()
    card.save(image_io, format='PNG')
    image_io.seek(0)

    # Send image as response
    response = HttpResponse(image_io, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{alumni.name}_profile.png"'
    return response

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
