from django.db import models

# Create your models here.

class attendance(models.Model):
    name=models.CharField(max_length=100)
    time=models.CharField(max_length=100)
