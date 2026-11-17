
from django.urls import path
from . import views

urlpatterns = [
    # Portfolio pages
    path('', views.home, name='home'),
    path('description/', views.description, name='description'),
    path('services/', views.services, name='services'),
    path('projects/', views.projects, name='projects'),
    path('experience/', views.experience, name='experience'),
    path('education/', views.education, name='education'),
    path('test-scores/', views.test_scores, name='test_scores'),
    path('certifications/', views.certifications, name='certifications'),
    path('languages/', views.languages, name='languages'),
    path('skills/', views.skills, name='skills'),
    path('hackathons/', views.hackathons, name='hackathons'),
    path('competitive-programming/', views.competitive_programming, name='competitive_programming'),
    path('contact/', views.contact_page, name='contact'),

    # Form submissions
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('submit-service-request/', views.submit_service_request, name='submit_service_request'),

    # Admin login
    path('secure-login/', views.custom_login, name='custom_login'),

    # Combined dashboard
    path('dashboard/', views.contact_dashboard, name='contact_dashboard'),

    # Contact message actions
    path('dashboard/message/<int:message_id>/', views.view_message, name='view_message'),
    path('dashboard/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('submit-rating/', views.submit_rating, name='submit_rating'),
]
