from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.TextField(default='', blank=True)
    age = models.TextField(default='', blank=True)
    current_budget = models.TextField(default='', blank=True)
    investment_goal = models.TextField(default='', blank=True)
    term_intended = models.TextField(default='', blank=True)
    rate_tolerance = models.TextField(default='', blank=True)
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class DailyWorth (models.Model):
    user = models.TextField()
    worth = models.IntegerField()
    timestamp = models.DateField(auto_now_add=True)
    

class Portfolio(models.Model):
    user = models.TextField()
    stock = models.CharField(max_length=25)
    number = models.IntegerField()

class Trading(models.Model):
    user = models.TextField()
    transaction_id = models.CharField(max_length=25)
    symbol = models.TextField()
    current_price_per_share = models.TextField()
    number_of_shares = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Stock(models.Model):
    stock = models.CharField(max_length=25)
    price = models.TextField()
    time_stamp = models.DateField(auto_now_add=True)

