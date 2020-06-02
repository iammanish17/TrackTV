from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Show(models.Model):
    showid = models.IntegerField()
    plot = models.TextField()
    status = models.CharField(max_length=32)


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    rating = models.IntegerField()
