from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Course
from .serializers import CourseSerializer
from .utils import validate_password_strength, is_valid_email_format


@api_view(['GET','POST'])
def course_list(request):
    if request.method == 'GET':
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def register(request):
    try:
        username = request.data['username'] #required
        password = request.data['password'] #required
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email', '') #optional
        if email and not is_valid_email_format(email):
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists(): #checks if username already exists
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST) 

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password) #Hashing the password
        )

        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    except KeyError:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({
        'message': f'Welcome, {request.user.username}! You are authenticated.'
    })