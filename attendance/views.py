from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, TeacherRegistration, StudentRegistration, Attendance, AdminDepartment
from .forms import CustomUserCreationForm, UserLoginForm, TeacherRegistrationForm, StudentRegistrationForm, AdminDepartmentForm
from .face_recognition_script import run_face_recognition  # Import the function
import base64
from io import BytesIO
from PIL import Image
from django.contrib import messages
from django.core.files.base import ContentFile
import base64
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def register(request):
    return render(request, 'attendance/register.html')


def index(request):
    return render(request, 'attendance/index.html')

def admin_department_list(request):
    departments = AdminDepartment.objects.all()
    return render(request, 'attendance/admin_department_list.html', {'departments': departments})

def admin_department_create(request):
    if request.method == 'POST':
        form = AdminDepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_department_list')
    else:
        form = AdminDepartmentForm()
    return render(request, 'attendance/admin_department_form.html', {'form': form})

def admin_department_detail(request, pk):
    department = get_object_or_404(AdminDepartment, pk=pk)
    return render(request, 'attendance/admin_department_detail.html', {'department': department})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = UserLoginForm()
    return render(request, 'attendance/User_log_in.html', {'form': form})




import logging
import json
import base64
import os
from io import BytesIO
from PIL import Image
from django.shortcuts import render, redirect
from .models import CustomUser, StudentRegistration
from .forms import CustomUserCreationForm, StudentRegistrationForm

logger = logging.getLogger(__name__)

def student_register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        student_form = StudentRegistrationForm(request.POST)

        if user_form.is_valid() and student_form.is_valid():
            try:
                user = user_form.save(commit=False)
                user.is_student = True
                user.save()

                student = student_form.save(commit=False)
                student.user = user
                student.save()

                # Handle the captured images
                captured_images = request.POST.get('captured_images')
                if (captured_images):
                    images = json.loads(captured_images)
                    face_images = []
                    
                    student_dir = f'media/students/{student.student_Enrollment}'
                    os.makedirs(student_dir, exist_ok=True)

                    for i, image_data in enumerate(images):
                        image_data = base64.b64decode(image_data.split(',')[1])
                        image = Image.open(BytesIO(image_data))
                        image_path = os.path.join(student_dir, f'face_{i + 1}.png')
                        image.save(image_path)
                        face_images.append(image_path)

                    student.face_images = face_images
                    student.save()

                logger.debug('Student registered successfully')
                return redirect('index')

            except Exception as e:
                logger.error(f'Error during student registration: {e}')
                logger.error(f'User form data: {user_form.cleaned_data}')
                logger.error(f'Student form data: {student_form.cleaned_data}')
        else:
            logger.error(f'User form errors: {user_form.errors}')
            logger.error(f'Student form errors: {student_form.errors}')

    else:
        user_form = CustomUserCreationForm()
        student_form = StudentRegistrationForm()

    return render(request, 'attendance/student_register.html', {
        'user_form': user_form,
        'student_form': student_form,
    })





def teacher_register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        teacher_form = TeacherRegistrationForm(request.POST)
        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save(commit=False)
            user.is_teacher = True
            user.set_password(teacher_form.cleaned_data['teacher_password'])
            user.save()
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.save()
            return redirect('index')
    else:
        user_form = CustomUserCreationForm()
        teacher_form = TeacherRegistrationForm()
    return render(request, 'attendance/teacher_register.html', {
        'user_form': user_form,
        'teacher_form': teacher_form,
    })




def user_logout(request):
    logout(request)
    return redirect('index')

def mark_attendance(request):
    students = StudentRegistration.objects.all()
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        for student in students:
            status = request.POST.get(f'attendance_{student.student_id}')
            attendance_record = AttendanceRecord(
                student_name=student.student_name,
                student_Enrollment=student.student_Enrollment,
                attendance_date=attendance_date,
                status=status
            )
            attendance_record.save()
        return redirect('attendance_success')
    return render(request, 'attendance/AttendanceMark.html', {'students': students})

from django.http import HttpResponse

def face_recognition_attendance(request):
    if request.method == 'POST':
        ip_cam_url = request.POST.get('ip_cam_url')
        if ip_cam_url:
            # Assuming student_id is passed in the POST request or can be determined
            student_id = request.POST.get('student_id')
            run_face_recognition(ip_cam_url, student_id)
            return HttpResponse("Face recognition started.")
        else:
            return HttpResponse("IP Camera URL is required.", status=400)
    return render(request, 'attendance/face_recognition.html')


def attendance_success(request):
    present_students = AttendanceRecord.objects.filter(status='Present')
    absent_students = AttendanceRecord.objects.filter(status='Absent')
    return render(request, 'attendance/attendance_success.html', {
        'present_students': present_students,
        'absent_students': absent_students
    })