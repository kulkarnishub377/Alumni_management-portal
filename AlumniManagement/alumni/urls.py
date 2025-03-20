from django.urls import path
from . import views
from .views import delete_alumni_confirm

# URL patterns for the alumni management application
urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Admin URLs
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/register/', views.admin_registration, name='admin_registration'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/manage_gallery_photos/', views.manage_gallery_photos_admin, name='manage_gallery_photos_admin'),
    path('admin/manage_comments/', views.manage_comments_admin, name='manage_comments_admin'),

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
    path('alumni_coordinator/export/', views.export_alumni_to_excel, name='export_alumni_to_excel'),
    path('coordinator/manage_gallery_photos/', views.manage_gallery_photos_coordinator, name='manage_gallery_photos_coordinator'),
    path('coordinator/manage_comments/', views.manage_comments_coordinator, name='manage_comments_coordinator'),

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
]