
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache
from portfolio.services.competitive import fetch_all_platforms

from .models import ContactMessage, ServiceRequest


# ==========================================
# PUBLIC PORTFOLIO PAGES
# ==========================================

def home(request):
    return render(request, 'portfolio/index.html', {'active_page': 'home'})


def description(request):
    return render(request, 'portfolio/description.html', {'active_page': 'description'})


def services(request):
    return render(request, 'portfolio/services.html', {'active_page': 'services'})


def projects(request):
    return render(request, 'portfolio/projects.html', {'active_page': 'projects'})


def experience(request):
    return render(request, 'portfolio/experience.html', {'active_page': 'experience'})


def education(request):
    return render(request, 'portfolio/education.html', {'active_page': 'education'})


def test_scores(request):
    return render(request, 'portfolio/test_scores.html', {'active_page': 'test_scores'})


def certifications(request):
    return render(request, 'portfolio/certifications.html', {'active_page': 'certifications'})


def languages(request):
    return render(request, 'portfolio/languages.html', {'active_page': 'languages'})


def skills(request):
    return render(request, 'portfolio/skills.html', {'active_page': 'skills'})


def hackathons(request):
    return render(request, 'portfolio/hackathons.html', {'active_page': 'hackathons'})


def competitive_programming(request):
    platform_data = cache.get("competitive_platform_data")

    if platform_data is None:
        platform_data = fetch_all_platforms()
        cache.set("competitive_platform_data", platform_data, 900)

    context = {
        "platform_data": platform_data,
    }

    return render(
        request,
        "portfolio/competitive_programming.html",
        context
    )


def contact_page(request):
    return render(request, 'portfolio/contact.html', {'active_page': 'contact'})


# ==========================================
# ADMIN LOGIN
# ==========================================

def custom_login(request):

    # Opening the login page always requires fresh authentication
    if request.method == 'GET':
        logout(request)
        return render(request, 'portfolio/login.html')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.is_active and user.is_staff:
            login(request, user)
            return redirect('contact_dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'portfolio/login.html')


# ==========================================
# COMBINED ADMIN DASHBOARD
# ==========================================

@login_required(login_url='custom_login')
def contact_dashboard(request):

    if not request.user.is_staff or not request.user.is_active:
        logout(request)
        return redirect('custom_login')

    query = request.GET.get('q', '').strip()

    # Contact messages
    contact_messages = ContactMessage.objects.all()

    # Service requests
    service_requests = ServiceRequest.objects.all()

    if query:
        contact_messages = contact_messages.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

        service_requests = service_requests.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(description__icontains=query)
        )

    # Separate pagination
    message_page = Paginator(contact_messages, 10).get_page(
        request.GET.get('message_page')
    )

    request_page = Paginator(service_requests, 10).get_page(
        request.GET.get('request_page')
    )

    return render(request, 'portfolio/dashboard.html', {
        'contact_messages': message_page,
        'service_requests': request_page,

        'message_page': message_page,
        'request_page': request_page,

        'query': query,

        'total_messages': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),

        'total_requests': ServiceRequest.objects.count(),
        'unread_requests': ServiceRequest.objects.filter(is_read=False).count(),
    })


# ==========================================
# CONTACT MESSAGE DETAILS
# ==========================================

@login_required(login_url='custom_login')
def view_message(request, message_id):

    if not request.user.is_staff or not request.user.is_active:
        logout(request)
        return redirect('custom_login')

    contact = get_object_or_404(ContactMessage, pk=message_id)

    if request.method == 'POST':
        contact.is_read = not contact.is_read
        contact.save(update_fields=['is_read'])
        return redirect('view_message', message_id=contact.pk)

    if not contact.is_read:
        contact.is_read = True
        contact.save(update_fields=['is_read'])

    return render(request, 'portfolio/message_detail.html', {
        'contact': contact
    })


# ==========================================
# DELETE CONTACT MESSAGE
# ==========================================

@login_required(login_url='custom_login')
@require_POST
def delete_message(request, message_id):

    if not request.user.is_staff or not request.user.is_active:
        logout(request)
        return redirect('custom_login')

    contact = get_object_or_404(ContactMessage, pk=message_id)
    contact.delete()

    messages.success(request, 'Message deleted successfully!')

    return redirect('contact_dashboard')


# ==========================================
# LOGOUT ENDPOINT (NOT DISPLAYED IN MENU)
# ==========================================

@login_required(login_url='custom_login')
@require_POST
def custom_logout(request):
    logout(request)
    return redirect('custom_login')


# ==========================================
# CONTACT EMAIL NOTIFICATION
# ==========================================

def send_contact_notification(contact):

    subject = f"New Portfolio Message: {contact.subject}"

    message = f"""
You have received a new message through your portfolio.

Name: {contact.name}
Email: {contact.email}
Subject: {contact.subject}

Message:
{contact.message}

Received at: {contact.created_at}
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
        fail_silently=False,
    )


# ==========================================
# CONTACT FORM SUBMISSION
# ==========================================

@require_POST
def submit_contact(request):

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not all([name, email, subject, message]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('contact')

    contact = ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    try:
        send_contact_notification(contact)
    except Exception as e:
        print("Email notification failed:", e)

    messages.success(request, 'Message sent successfully!')

    return redirect('contact')


# ==========================================
# SERVICE REQUEST SUBMISSION
# ==========================================


def submit_service_request(request):
    if request.method != 'POST':
        return redirect('services')

    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    service_type = request.POST.get('service_type', '').strip()
    description = request.POST.get('description', '').strip()

    preferred_language = request.POST.get(
        'preferred_language', 'none'
    ).strip()

    country = request.POST.get('country', '').strip()
    state_region = request.POST.get('state_region', '').strip()
    district = request.POST.get('district', '').strip()

    # Validate required fields.
    if not all([
        name, phone, service_type, description,
        country, state_region
    ]):
        messages.error(request, 'Please complete all required fields.')
        return redirect('services')

    valid_languages = {
        'none', 'ta', 'en', 'hi', 'te', 'kn', 'ml'
    }

    if preferred_language not in valid_languages:
        messages.error(request, 'Please select a valid language.')
        return redirect('services')

    valid_services = dict(ServiceRequest.SERVICE_CHOICES)

    if service_type not in valid_services:
        messages.error(request, 'Please select a valid service.')
        return redirect('services')

    if country == 'India' and not district:
        messages.error(request, 'Please select your district.')
        return redirect('services')

    if country != 'India':
        district = ''

    ServiceRequest.objects.create(
        name=name,
        phone=phone,
        email=email,
        service_type=service_type,
        description=description,
        preferred_language=preferred_language,
        country=country,
        state_region=state_region,
        district=district
    )

    messages.success(
        request,
        'Your service enquiry has been submitted successfully!'
    )

    return redirect('services')
