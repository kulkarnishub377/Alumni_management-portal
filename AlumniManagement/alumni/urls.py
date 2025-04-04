from django.urls import path
from . import views
from .views import delete_alumni_confirm, verify_details, verify_otp, reset_password, download_notice_media, get_graduation_years

# URL patterns for the alumni management application
urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Alumni URLs
    path('alumni/register/', views.alumni_registration, name='alumni_registration'),
    path('alumni/profile/', views.alumni_profile, name='alumni_profile'),
    path('alumni/edit-profile/', views.alumni_edit_profile, name='alumni_edit_profile'),
    path('alumni/share/<int:id>/', views.share_alumni_profile, name='share_alumni_profile'),
    path('alumni/edit/<int:id>/', views.edit_alumni, name='edit_alumni'),
    path('alumni/delete/<str:id>/', views.delete_alumni, name='delete_alumni'),
    path('alumni/login/', views.alumni_login, name='alumni_login'),

    # Alumni Coordinator URLs
    path('alumni_coordinator/login/', views.alumni_coordinator_login, name='alumni_coordinator_login'),
    path('alumni_coordinator/register/', views.alumni_coordinator_registration, name='alumni_coordinator_registration'),
    path('alumni_coordinator/dashboard/', views.alumni_coordinator_dashboard, name='alumni_coordinator_dashboard'),
    path('alumni_coordinator/edit-profile/', views.edit_coordinator_profile, name='edit_coordinator_profile'),
    path('coordinator/manage_gallery_photos/', views.manage_gallery_photos_coordinator, name='manage_gallery_photos_coordinator'),
    path('coordinator/manage_comments/', views.manage_comments_coordinator, name='manage_comments_coordinator'),
    path('alumni-coordinator/manage-batch-mentors/', views.manage_batch_mentors, name='manage_batch_mentors'),
    path('alumni-coordinator/edit-mentor/<int:id>/', views.edit_mentor, name='edit_mentor'),
    path('alumni-coordinator/delete-mentor/<int:id>/', views.delete_mentor, name='delete_mentor'),
    path('alumni_coordinator/send_email_notification/', views.send_email_notification, name='send_email_notification'),

    # Batch Mentor URLs
    path('batch-mentor/register/', views.batch_mentor_registration, name='batch_mentor_register'),
    path('batch-mentor/login/', views.batch_mentor_login, name='batch_mentor_login'),  # Updated name
    path('batch-mentor/dashboard/', views.batch_mentor_dashboard, name='batch_mentor_dashboard'),

    # Gallery URLs
    path('gallery/', views.gallery, name='gallery'),
    path('add_gallery_photo/', views.add_gallery_photo, name='add_gallery_photo'),
    path('delete_gallery_photo/<int:id>/', views.delete_gallery_photo, name='delete_gallery_photo'),

    # Comment URLs
    path('add_comment/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:id>/', views.delete_comment, name='delete_comment'),

    # Miscellaneous URLs
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about_us, name='about_us'),

    # Delete confirmation URL
    path('delete_alumni_confirm/<int:id>/', delete_alumni_confirm, name='delete_alumni_confirm'),

    # Assign batch URL
    path('assign_batch/<int:mentor_id>/', views.assign_batch, name='assign_batch'),

    # Remove assigned batch URL
    path('remove_assigned_batch/<int:mentor_id>/<int:year_id>/', views.remove_assigned_batch, name='remove_assigned_batch'),

    # Verification URLs
    path('verify-details/', verify_details, name='verify_details'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),

    # Resend OTP URL
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    # Notice management URLs
    path('manage-notices/', views.manage_notices, name='manage_notices'),
    path('add-notice/', views.add_notice, name='add_notice'),
    path('delete-notice/<int:id>/', views.delete_notice, name='delete_notice'),
    path('download-notice-media/<int:notice_id>/', download_notice_media, name='download_notice_media'),
    
    # Event management URLs
    path('manage-events/', views.manage_events, name='manage_events'),
    path('add-event/', views.add_event, name='add_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('download-event-media/<int:event_id>/', views.download_event_media, name='download_event_media'),

    # API URLs
    path('api/graduation_years/', get_graduation_years, name='get_graduation_years'),
]