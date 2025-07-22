from django.db import models

class Course(models.Model):
    course_code= models.CharField(max_length=15)
    course_name= models.CharField(max_length=100)
    course_description= models.TextField(blank=True)
    course_credits= models.IntegerField()
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

