import os
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
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

    return render(
        request,
        "portfolio/competitive_programming.html",
        {"platform_data": platform_data}
    )


def contact_page(request):
    return render(request, 'portfolio/contact.html', {'active_page': 'contact'})


# ==========================================
# DASHBOARD AUTHENTICATION
# ==========================================

def dashboard_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('dashboard_authenticated'):
            return redirect('custom_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def custom_login(request):
    if request.method == 'GET':
        request.session.flush()
        return render(request, 'portfolio/login.html')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        correct_username = os.environ.get('DASHBOARD_USERNAME')
        correct_password = os.environ.get('DASHBOARD_PASSWORD')

        if not correct_username or not correct_password:
            messages.error(request, 'Login is temporarily unavailable.')
            return render(request, 'portfolio/login.html')

        if username == correct_username and password == correct_password:
            request.session['dashboard_authenticated'] = True
            request.session.set_expiry(1800)
            return redirect('contact_dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'portfolio/login.html')


# ==========================================
# COMBINED ADMIN DASHBOARD
# ==========================================

@dashboard_required
def contact_dashboard(request):
    query = request.GET.get('q', '').strip()

    contact_messages = ContactMessage.objects.all()
    service_requests = ServiceRequest.objects.all()

    if query:
        contact_messages = contact_messages.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

        service_requests = service_requests.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(description__icontains=query)
        )

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

@dashboard_required
def view_message(request, message_id):
    contact = get_object_or_404(ContactMessage, pk=message_id)

    if request.method == 'POST':
        contact.is_read = not contact.is_read
        contact.save(update_fields=['is_read'])
        return redirect('view_message', message_id=contact.pk)

    if not contact.is_read:
        contact.is_read = True
        contact.save(update_fields=['is_read'])

    return render(request, 'portfolio/message_detail.html', {'contact': contact})


# ==========================================
# DELETE CONTACT MESSAGE
# ==========================================

@dashboard_required
@require_POST
def delete_message(request, message_id):
    contact = get_object_or_404(ContactMessage, pk=message_id)
    contact.delete()
    messages.success(request, 'Message deleted successfully!')
    return redirect('contact_dashboard')


# ==========================================
# LOGOUT ENDPOINT
# ==========================================

@dashboard_required
@require_POST
def custom_logout(request):
    request.session.flush()
    return redirect('custom_login')


# ==========================================
# EMAIL NOTIFICATION FUNCTIONS
# ==========================================

def send_portfolio_notification(subject, message):
    """Send an email notification to the portfolio owner."""
    recipient = settings.CONTACT_NOTIFICATION_EMAIL
    sender = settings.DEFAULT_FROM_EMAIL

    if not recipient or not sender or not settings.EMAIL_HOST_PASSWORD:
        raise ValueError(
            "Email configuration is incomplete. Check "
            "EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and "
            "CONTACT_NOTIFICATION_EMAIL."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=sender,
        recipient_list=[recipient],
        fail_silently=False,
    )


def send_contact_notification(contact):
    subject = f"New Portfolio Message: {contact.subject}"
    message = f"""
You have received a new message through your portfolio.

Name: {contact.name}
Phone: {contact.phone}
Subject: {contact.subject}

Message:
{contact.message}

Received at: {contact.created_at}
"""
    send_portfolio_notification(subject, message)


def send_service_request_notification(service):
    subject = f"New Service Request: {service.service_type}"
    message = f"""
You have received a new service request through your portfolio.

Name: {service.name}
Phone: {service.phone}
Email: {service.email}

Service: {service.service_type}

Description:
{service.description}

Preferred Language: {service.preferred_language}

Country: {service.country}
State / Region: {service.state_region}
District: {service.district}

Received at: {service.created_at}
"""
    send_portfolio_notification(subject, message)


# ==========================================
# CONTACT FORM SUBMISSION
# ==========================================

@require_POST
def submit_contact(request):
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not all([name, phone, subject, message]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('contact')

    contact = ContactMessage.objects.create(
        name=name,
        phone=phone,
        subject=subject,
        message=message,
    )

    try:
        send_contact_notification(contact)
        print("Contact notification email sent successfully.")
    except Exception as e:
        # Preserve the database record if email delivery fails.
        print("Contact notification email failed:", repr(e))

    messages.success(request, 'Message sent successfully!')
    return redirect('contact')


# ==========================================
# SERVICE REQUEST SUBMISSION
# ==========================================

@require_POST
def submit_service_request(request):
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()

    service_type = request.POST.get('service_type', '').strip()
    description = request.POST.get('description', '').strip()
    preferred_language = request.POST.get('preferred_language', 'none').strip()
    country = request.POST.get('country', '').strip()
    state_region = request.POST.get('state_region', '').strip()
    district = request.POST.get('district', '').strip()

    if not all([name, phone, service_type, description, country, state_region]):
        messages.error(request, 'Please complete all required fields.')
        return redirect('services')

    valid_languages = {'none', 'ta', 'en', 'hi', 'te', 'kn', 'ml'}
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

    service = ServiceRequest.objects.create(
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

    try:
        send_service_request_notification(service)
        print("Service request notification email sent successfully.")
    except Exception as e:
        # Preserve the database record if email delivery fails.
        print("Service request notification email failed:", repr(e))

    messages.success(
        request,
        'Your service enquiry has been submitted successfully!'
    )
    return redirect('services')
