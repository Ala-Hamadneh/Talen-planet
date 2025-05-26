from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class UserRoles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_roles'
    
    def __str__(self):
        return self.role_name

class User(AbstractUser):
    # Map Django's default fields to your schema
    id = models.AutoField(primary_key=True, db_column='user_id')
    
    # Keep your existing fields
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    role = models.ForeignKey(UserRoles, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='role_id')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Remove unused AbstractUser fields
    first_name = None
    last_name = None
    
    is_verified = models.BooleanField(default=False)
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username

    @property
    def average_rating(self):
        return self.received_reviews.filter(is_active=True).aggregate(avg=Avg('rating'))['avg'] or 0

    @property
    def reviews_count(self):
        return self.received_reviews.filter(is_active=True).count()
    

class EmailVerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)