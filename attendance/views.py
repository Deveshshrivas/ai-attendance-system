from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, TeacherRegistration, StudentRegistration, AttendanceRecord
from .forms import CustomUserCreationForm, UserLoginForm, TeacherRegistrationForm, StudentRegistrationForm, AdminDepartmentForm


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


def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        student_form = None
        teacher_form = None
        if user_form.is_valid():
            user = user_form.save(commit=False)
            if user.is_student:
                student_form = StudentRegistrationForm(request.POST, request.FILES)
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user
                    user.set_password(student_form.cleaned_data['student_password'])  # Set the password
                    user.save()
                    student.save()
            elif user.is_teacher:
                teacher_form = TeacherRegistrationForm(request.POST)
                if teacher_form.is_valid():
                    teacher = teacher_form.save(commit=False)
                    teacher.user = user
                    user.set_password(teacher_form.cleaned_data['teacher_password'])  # Set the password
                    user.save()
                    teacher.save()
            return redirect('index')
    else:
        user_form = CustomUserCreationForm()
        student_form = StudentRegistrationForm()
        teacher_form = TeacherRegistrationForm()
    return render(request, 'attendance/register.html', {
        'user_form': user_form,
        'student_form': student_form,
        'teacher_form': teacher_form
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


def face_recognition_attendance(request):
    run_face_recognition()
    return redirect('attendance_success')

def attendance_success(request):
    present_students = AttendanceRecord.objects.filter(status='Present')
    absent_students = AttendanceRecord.objects.filter(status='Absent')
    return render(request, 'attendance/attendance_success.html', {
        'present_students': present_students,
        'absent_students': absent_students
    })