from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Register(models.Model):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ]
    
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    role=models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant', null=True)
    gen=models.CharField(max_length=30,null=True)
    add=models.CharField(max_length=100,null=True)
    mobile=models.CharField(max_length=10,null=True)
    image=models.FileField(null=True)
    birth=models.DateField(null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.CharField(max_length=200, blank=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)
    min_rent = models.IntegerField(null=True, blank=True)
    max_rent = models.IntegerField(null=True, blank=True)
    viewed_room = models.ForeignKey('Owner_Detail', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.search_query or 'No query'}"

class State(models.Model):
    state=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.state


class District(models.Model):
    state=models.ForeignKey(State,on_delete=models.CASCADE,null=True)
    dist=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.dist+" "+self.state.state


class Area(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    area_name = models.CharField(max_length=100, null=True)
    
    class Meta:
        verbose_name_plural = "Areas"
    
    def __str__(self):
        if self.district:
            return f"{self.area_name} - {self.district.dist}"
        return self.area_name


class Status(models.Model):
    status = models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.status


class Owner_Detail(models.Model):
    status = models.ForeignKey(Status,on_delete=models.CASCADE,null=True)
    register=models.ForeignKey(Register,on_delete=models.CASCADE,null=True)
    state=models.ForeignKey(State,on_delete=models.CASCADE,null=True)
    dist=models.ForeignKey(District,on_delete=models.CASCADE,null=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    local_add = models.CharField(max_length=100,null=True)
    title=models.CharField(max_length=100,null=True)
    desc=models.CharField(max_length=100,null=True)
    rent=models.IntegerField(null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    img=models.FileField(null=True)

    def __str__(self):
        return self.register.user.username


class Image(models.Model):
    owner=models.ForeignKey(Owner_Detail,on_delete=models.CASCADE,null=True)
    room_name=models.CharField(max_length=100,null=True)
    img=models.FileField(null=True)
    def __str__(self):
        return self.owner.register.user.username+" "+self.room_name





