from django.db import models
from django.contrib.auth.models import User

class PlannedCourse(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    course_code= models.CharField(max_length=15)
    course_name= models.CharField(max_length=100)
    course_description= models.TextField(blank=True)
    course_credits= models.DecimalField(max_digits=5, decimal_places=1)
    source= models.CharField(max_length=10,choices=[('manual', 'Manual'), ('dars', 'DARS')],
        default='manual')
    def __str__(self):
        return f"{self.code} - {self.name} ({self.user.username})"


