from django.db import models
from django.conf import settings
# Create your models here.

class Venue(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sport_type = models.CharField(
        max_length=50,
        choices=[
            ('football', 'Football'),
            ('basketball', 'Basketball'),
            ('tennis', 'Tennis'),
            ('padel', 'Padel')
        ]
    )
    city = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=200)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    amenities = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True, default='images/default.jpg')  

    def __str__(self):
        
        return f"{self.name} ({self.sport_type})"