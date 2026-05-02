from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

# =====================================================================
# User Profile Model (Merged Register + UserProfile into single model)
# =====================================================================

class UserProfile(models.Model):
    """Extended user profile with role, contact, and personal information."""
    
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='tenant',
        help_text='User role: tenant or landlord'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', 'Phone must be 10 digits')],
        help_text='10-digit phone number'
    )
    address = models.TextField(
        max_length=300,
        blank=True,
        null=True,
        help_text='User address'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date of birth'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='Short biography'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
        db_table = 'userprofile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    def is_landlord(self):
        return self.role == 'landlord'

    def is_tenant(self):
        return self.role == 'tenant'


# Signal to save UserProfile when User is saved
# NOTE: Auto-creation of UserProfile is handled by signup views
# to properly set the role (tenant/landlord) at signup time
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


# =====================================================================
# Location Models (State, District, Area hierarchy)
# =====================================================================

class State(models.Model):
    """State/Region model."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='State or region name'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'States'
        ordering = ['name']
        db_table = 'state'

    def __str__(self):
        return self.name


class District(models.Model):
    """District model linked to State."""
    
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='districts',
        help_text='State this district belongs to'
    )
    name = models.CharField(
        max_length=100,
        help_text='District name'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Districts'
        unique_together = ('state', 'name')
        ordering = ['state', 'name']
        db_table = 'district'
        indexes = [
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.name} - {self.state.name}"


class Area(models.Model):
    """Area/Locality model linked to District (removed redundant State FK)."""
    
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='areas',
        help_text='District this area belongs to'
    )
    name = models.CharField(
        max_length=100,
        help_text='Area or locality name'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Areas'
        unique_together = ('district', 'name')
        ordering = ['district', 'name']
        db_table = 'area'
        indexes = [
            models.Index(fields=['district']),
        ]

    def __str__(self):
        return f"{self.name} - {self.district.name}"


# =====================================================================
# Property Model (Replaces Owner_Detail with improved structure)
# =====================================================================

class Property(models.Model):
    """Rental property listing model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Landlord / Owner
    landlord = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties',
        help_text='Landlord who owns this property'
    )

    # Property Details
    title = models.CharField(
        max_length=200,
        help_text='Property title/name'
    )
    description = models.TextField(
        max_length=2000,
        help_text='Detailed property description'
    )
    rent = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Monthly rent amount (must be > 0)'
    )

    # Location Details
    address = models.TextField(
        max_length=500,
        help_text='Complete address of the property'
    )
    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties',
        help_text='State where property is located'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        related_name='properties',
        help_text='District where property is located'
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        help_text='Area/locality where property is located'
    )

    # Geographic Coordinates
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        null=True,
        blank=True,
        help_text='Latitude (-90 to 90)'
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        null=True,
        blank=True,
        help_text='Longitude (-180 to 180)'
    )

    # Featured Image
    featured_image = models.ImageField(
        upload_to='properties/',
        help_text='Main property image'
    )

    # Status and Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Approval status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        db_table = 'property'
        indexes = [
            models.Index(fields=['landlord']),
            models.Index(fields=['status']),
            models.Index(fields=['district']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.district.name} (₹{self.rent}/month)"

    def get_status_display_short(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def is_approved(self):
        return self.status == 'approved'

    def is_pending(self):
        return self.status == 'pending'

    def is_rejected(self):
        return self.status == 'rejected'


# =====================================================================
# Property Image Model (Replaces Image model with better naming)
# =====================================================================

class PropertyImage(models.Model):
    """Additional images for a property listing."""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Property this image belongs to'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text='Image title (e.g., "Bedroom", "Kitchen")'
    )
    image = models.ImageField(
        upload_to='property_images/',
        help_text='Property image'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Property Images'
        ordering = ['uploaded_at']
        db_table = 'propertyimage'
        indexes = [
            models.Index(fields=['property']),
        ]

    def __str__(self):
        return f"{self.title or 'Image'} - {self.property.title}"


# =====================================================================
# User Search History Model (For recommendations & analytics)
# =====================================================================

class UserSearchHistory(models.Model):
    """Track user searches for analytics and recommendations."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='search_history',
        help_text='User who performed the search'
    )
    search_query = models.CharField(
        max_length=300,
        blank=True,
        help_text='Search query text'
    )
    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_history',
        help_text='State searched'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_history',
        help_text='District searched'
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_history',
        help_text='Area searched'
    )
    min_rent = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Minimum rent filter'
    )
    max_rent = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Maximum rent filter'
    )
    viewed_property = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='views_history',
        help_text='Property viewed'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name_plural = 'Search Histories'
        ordering = ['-timestamp']
        db_table = 'usersearchhistory'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['district']),
        ]

    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        query = self.search_query[:30] if self.search_query else 'No query'
        return f"{username} - {query} ({self.timestamp.strftime('%Y-%m-%d')})"






