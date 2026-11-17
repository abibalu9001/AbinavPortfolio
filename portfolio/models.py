
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, default='')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class ServiceRequest(models.Model):

    SERVICE_CHOICES = [
        ('ai_ml', 'AI & Machine Learning'),
        ('web', 'Full-Stack Web Development'),
        ('data', 'Data Analysis & Visualization'),
        ('iot', 'IoT & Hardware Development'),
        ('math', 'Mathematical Research'),
        ('consultation', 'Technical Consultation'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, default='')
    email = models.EmailField(blank=True)

    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES
    )

    description = models.TextField(max_length=2000)

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    PREFERRED_LANGUAGE_CHOICES = [
        ('none', 'No preference'),
        ('ta', 'Tamil'),
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
    ]

    preferred_language = models.CharField(
        max_length=20,
        choices=PREFERRED_LANGUAGE_CHOICES,
        default='none'
    )

    country = models.CharField(max_length=100, default='')

    state_region = models.CharField(max_length=100, default='')

    district = models.CharField(max_length=100, blank=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_service_type_display()}"

class SiteStats(models.Model):
    total_visits = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Website Visits: {self.total_visits}"


class SiteRating(models.Model):
    visitor_key = models.UUIDField(unique=True)
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}/5"
