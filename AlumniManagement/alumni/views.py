import sys
from django.http import HttpResponse, JsonResponse
sys.setrecursionlimit(10000)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import Alumni, AlumniCoordinator, Comment, GalleryPhoto, BatchMentor, GraduationYear
from .forms import (
    AdminRegistrationForm, AlumniRegistrationForm, AlumniCoordinatorRegistrationForm,
    AlumniEditForm, GalleryPhotoForm, CommentForm, AlumniCoordinatorEditForm,
    BatchMentorRegistrationForm, BatchMentorLoginForm
)
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path
from django import forms
from .import views
from django.template.loader import render_to_string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import logging
import json
from django.core.mail import send_mail
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

otp_storage = {}

# Home Page
def home(request):
    return render(request, 'home.html')

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
        # Ensure profile_photo is handled gracefully
        if not alumni.profile_photo:
            alumni.profile_photo = None  # Placeholder logic if needed
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
    alumni = get_object_or_404(Alumni, id=id)
    if request.method == 'POST':
        form = AlumniEditForm(request.POST, request.FILES, instance=alumni)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('alumni_coordinator_dashboard')
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
    alumni = get_object_or_404(Alumni, id=id)
    alumni.delete()
    return redirect('alumni_coordinator_dashboard')

# Delete Alumni with Confirmation
def delete_alumni_confirm(request, id):
    alumni = get_object_or_404(Alumni, id=id)
    if request.method == 'POST':
        alumni.delete()
        return redirect('alumni_coordinator_dashboard')
    return render(request, 'alumni_coordinator/delete_alumni_confirm.html', {'alumni': alumni})

from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from .models import Alumni

def share_alumni_profile(request, id):
    try:
        alumni = Alumni.objects.get(pk=id)
        
        # Paths for images
        base_dir = os.path.dirname(__file__)
        header_image_path = os.path.join(base_dir, 'static', 'images', 'header-2.jpg')
        watermark_image_path = os.path.join(base_dir, 'static', 'images', 'back.jpg')

        # Create A4-sized image
        image = Image.new('RGBA', (1240, 1754), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Load fonts
        font_regular = ImageFont.truetype("arial.ttf", 28)
        font_bold = ImageFont.truetype("arialbd.ttf", 34)
        font_title = ImageFont.truetype("arialbd.ttf", 50)

        # Draw header image
        try:
            header_image = Image.open(header_image_path).resize((1240, 200))
            image.paste(header_image, (0, 0))
        except FileNotFoundError:
            draw.rectangle([(0, 0), (1240, 200)], fill=(30, 144, 255))
            draw.text((400, 80), "ALUMNI PROFILE", fill="white", font=font_title)

        # Apply watermark
        try:
            watermark = Image.open(watermark_image_path).convert("RGBA")
            watermark = watermark.resize((image.width // 3, image.height // 3))  # Resize watermark to 50%
            watermark.putalpha(50)  # Set transparency

            # Position watermark at the center
            wm_x = (image.width - watermark.width) // 2
            wm_y = (image.height - watermark.height) // 2
            image.paste(watermark, (wm_x, wm_y), watermark)
        except FileNotFoundError:
            pass

        # Draw profile picture
        try:
            profile_photo = Image.open(alumni.profile_photo.path).resize((220, 220)).convert("RGBA")
            mask = Image.new("L", (220, 220), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 220, 220), fill=255)
            image.paste(profile_photo, (510, 230), mask)
        except FileNotFoundError:
            draw.text((560, 280), "No Photo", fill="red", font=font_bold)

        # Draw full name
        full_name_bbox = draw.textbbox((0, 0), alumni.full_name, font=font_title)
        full_name_position = (image.width // 2 - (full_name_bbox[2] - full_name_bbox[0]) // 2, 480)
        draw.text(full_name_position, alumni.full_name, fill="black", font=font_title)

        # Draw profile details
        y_offset = 550
        spacing = 60
        text_color = (0, 0, 0)

        def draw_label(position, label, value):
            """Draws a label and value with a slight shadow effect for better visibility."""
            shadow_offset = 2
            draw.text((position[0] + shadow_offset, position[1] + shadow_offset), f"{label}:", fill=(180, 180, 180), font=font_bold)
            draw.text(position, f"{label}:", fill=(30, 144, 255), font=font_bold)
            draw.text((position[0] + 300 + shadow_offset, position[1] + shadow_offset), value if value else "N/A", fill=(180, 180, 180), font=font_regular)
            draw.text((position[0] + 300, position[1]), value if value else "N/A", fill=text_color, font=font_regular)

        details = [
            ("Email", alumni.email),
            ("Mobile", alumni.mobile),
            ("ID", str(alumni.id)),
            ("Current Job", alumni.current_job_profile),
            ("Company", alumni.current_company),
            ("Location", alumni.current_job_location),
            ("City", alumni.city),
            ("State", alumni.state),
            ("Pincode", alumni.pincode),
            ("Country", alumni.country),
            ("Graduation Year", str(alumni.graduation_year)),
            ("Experience", f"{alumni.experience} years"),
            ("Sector", alumni.sector),
        ]

        # Add bullet points to the labels
        details = [(f"• {label}", value) for label, value in details]

        for label, value in details:
            draw_label((100, y_offset), label, value)
            y_offset += spacing

        # Social Media Links
        y_offset += 40
        draw.text((100, y_offset), "Social Links", fill="black", font=font_bold)
        y_offset += 40
        social_links = [
            ("LinkedIn", alumni.linkedin),
            ("Facebook", alumni.facebook),
            ("Instagram", alumni.instagram),
            ("GitHub", alumni.github),
        ]

        for platform, link in social_links:
            if link:
                draw_label((100, y_offset), platform, link)
                y_offset += spacing

        # Convert image to JPEG response
        response = HttpResponse(content_type="image/jpeg")
        image = image.convert("RGB")
        image.save(response, "JPEG", quality=100)
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


def custom_404(request, exception=None):
    logger.error(f"404 Not Found: {request.path}")
    return render(request, '404.html', status=404)

def profile_view(request, slug):
    alumni = get_object_or_404(Alumni, slug=slug)
    return render(request, 'alumni/profile_view.html', {'alumni': alumni})

# Batch Mentor Registration
def batch_mentor_registration(request):
    if request.method == 'POST':
        form = BatchMentorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch Mentor registered successfully.')
            return redirect('batch_mentor_login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BatchMentorRegistrationForm()
    return render(request, 'batch_mentor/registration.html', {'form': form})

# Batch Mentor Login
def batch_mentor_login(request):
    if request.method == 'POST':
        form = BatchMentorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                mentor = BatchMentor.objects.get(email=email)
                if mentor.check_password(password):
                    request.session['mentor_id'] = mentor.id
                    return redirect('batch_mentor_dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except BatchMentor.DoesNotExist:
                messages.error(request, 'Mentor not found.')
    else:
        form = BatchMentorLoginForm()
    return render(request, 'batch_mentor/login.html', {'form': form})

# Batch Mentor Dashboard
def batch_mentor_dashboard(request):
    if 'mentor_id' not in request.session:
        return redirect('batch_mentor_login')
    mentor = BatchMentor.objects.get(pk=request.session['mentor_id'])
    alumni_list = Alumni.objects.filter(graduation_year__in=mentor.assigned_batches.values_list('year', flat=True))  # Use 'year' instead of 'graduation_year'
    return render(request, 'batch_mentor/dashboard.html', {'mentor': mentor, 'alumni_list': alumni_list})

# Assign Batch
def assign_batch(request, mentor_id):
    if request.method == 'POST':
        mentor = get_object_or_404(BatchMentor, id=mentor_id)
        graduation_year = request.POST.get('graduation_year')
        if graduation_year:
            # Ensure graduation_year is an integer
            graduation_year = int(graduation_year)
            # Get or create the GraduationYear instance
            year_instance, created = GraduationYear.objects.get_or_create(year=graduation_year)
            mentor.assigned_batches.add(year_instance)  # Add GraduationYear instance
            messages.success(request, f'Graduation Year {graduation_year} assigned to {mentor.full_name}.')
        else:
            messages.error(request, 'No graduation year selected.')
        return redirect('manage_batch_mentors')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('manage_batch_mentors')

# Remove Assigned Batch
def remove_assigned_batch(request, mentor_id, year_id):
    mentor = get_object_or_404(BatchMentor, id=mentor_id)
    year_instance = get_object_or_404(GraduationYear, id=year_id)
    mentor.assigned_batches.remove(year_instance)  # Remove the GraduationYear instance
    messages.success(request, f'Graduation Year {year_instance.year} removed from {mentor.full_name}.')
    return redirect('manage_batch_mentors')

# Manage Batch Mentors
def manage_batch_mentors(request):
    if 'coordinator_id' not in request.session:
        return redirect('alumni_coordinator_login')  # Ensure proper redirection
    mentors = BatchMentor.objects.all()
    graduation_years = Alumni.objects.values_list('graduation_year', flat=True).distinct()  # Fetch unique graduation years
    return render(request, 'alumni_coordinator/manage_batch_mentors.html', {'mentors': mentors, 'graduation_years': graduation_years})

# Edit Mentor
def edit_mentor(request, id):
    mentor = get_object_or_404(BatchMentor, id=id)
    if request.method == 'POST':
        form = BatchMentorRegistrationForm(request.POST, request.FILES, instance=mentor)
        if form.is_valid():
            mentor = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if password1 and password1 == password2:
                mentor.set_password(password1)
            mentor.save()
            messages.success(request, 'Mentor updated successfully.')
            return redirect('manage_batch_mentors')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BatchMentorRegistrationForm(instance=mentor)
    return render(request, 'alumni_coordinator/edit_mentor.html', {'form': form, 'mentor': mentor})

# Delete Mentor
def delete_mentor(request, id):
    mentor = get_object_or_404(BatchMentor, id=id)
    if request.method == 'POST':
        mentor.delete()
        messages.success(request, 'Mentor deleted successfully.')
        return redirect('manage_batch_mentors')
    return render(request, 'alumni_coordinator/manage_batch_mentors.html', {'mentors': BatchMentor.objects.all()})

# Verify Details
def verify_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        mobile = data.get('phone')
        user_type = data.get('user_type')  # Added user_type to distinguish between users

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'error': 'Invalid email address.'})

        try:
            if user_type == 'batch_mentor':
                user = BatchMentor.objects.get(email=email, mobile=mobile)
            else:
                user = Alumni.objects.get(email=email, mobile=mobile)

            otp = random.randint(100000, 999999)
            otp_storage[email] = otp
            request.session['email'] = email
            send_mail(
                'Password Reset OTP - Alumni Management System',
                f"Dear User,\n\n"
                f"We received a request to reset your password for your account associated with this email address. "
                f"To proceed, please use the One-Time Password (OTP) provided below:\n\n"
                f"OTP: {otp}\n\n"
                f"Please note that this OTP is valid for only 2 minutes. If you did not request a password reset, "
                f"please ignore this email or contact our support team immediately.\n\n"
                f"Thank you for using the Alumni Management System.\n\n"
                f"Best regards,\n"
                f"Alumni Management Team",
                'noreply@alumnimanagement.com',
                [email]
            )
            return JsonResponse({'success': True})
        except (BatchMentor.DoesNotExist, Alumni.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid email or phone number.'})

def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        otp = data.get('otp')  # Ensure OTP is retrieved as a string
        email = request.session.get('email')  # Retrieve email from session

        if email in otp_storage and otp_storage[email] == int(otp):  # Compare OTP as an integer
            del otp_storage[email]  # Remove OTP after successful verification
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid OTP.'})

# Reset Password
def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('newPassword')
        email = request.session.get('email')

        try:
            alumni = Alumni.objects.get(email=email)
            alumni.set_password(new_password)
            alumni.save()
            return JsonResponse({'success': True})
        except Alumni.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found.'})

def resend_otp(request):
    if request.method == 'POST':
        # Logic to resend OTP (e.g., send OTP to user's email or phone)
        # For now, we'll simulate success.
        return JsonResponse({'success': True, 'message': 'OTP resent successfully.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
