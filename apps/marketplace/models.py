from django.db import models
from django.db.models import Avg
from django.conf import settings

# Create your models here.

class Categories(models.Model):
    name = models.CharField(max_length=50,unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        db_table = "categories"

    def __str__(self):
        return self.name

class Services(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('Categories' ,on_delete=models.CASCADE,related_name='services')

    class Meta:
        db_table = "services"

    def __str__(self):
        return self.name
    
class Gigs(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gigs')
    service = models.ForeignKey('Services', on_delete=models.CASCADE, related_name='gigs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField()  # in days
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='gig_images/', blank=True, null=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_gigs', blank=True)
    class Meta:
        db_table = "gigs"

    def __str__(self):
        return self.title
    @property
    def average_rating(self):
        return self.reviews.filter(is_active=True).aggregate(avg=Avg('rating'))['avg'] or 0
    @property
    def reviews_count(self):
        return self.reviews.filter(is_active=True).count()