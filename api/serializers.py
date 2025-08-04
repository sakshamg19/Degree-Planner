from rest_framework import serializers
from .models import PlannedCourse

class PlannedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannedCourse
        fields = '__all__'
        read_only_fields = ['user','source']