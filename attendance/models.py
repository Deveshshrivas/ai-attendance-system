from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

def student_image_upload_path(instance, filename):
    return f'students/{instance.student_Enrollment}/{filename}'

class AdminDepartment(models.Model):
    Admin_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=100)
    department_description = models.TextField()
    department_head = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class AttendanceRecord(models.Model):
    student_name = models.CharField(max_length=100)
    student_Enrollment = models.CharField(max_length=100)
    attendance_date = models.DateField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student_name} ({self.student_Enrollment}) - {self.attendance_date} - {self.status}"

class TeacherRegistration(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department_id = models.CharField(max_length=15)
    department_code = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)
    teacher_email = models.EmailField()
    teacher_phone = models.CharField(max_length=15)
    teacher_address = models.TextField()
    teacher_password = models.CharField(max_length=100)

    def __str__(self):
        return self.teacher_name

class StudentRegistration(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department_id = models.CharField(max_length=15)
    department_code = models.CharField(max_length=100)
    student_Enrollment = models.CharField(max_length=15)
    student_name = models.CharField(max_length=100)
    student_email = models.EmailField()
    student_phone = models.CharField(max_length=15)
    student_address = models.TextField()
    student_password = models.CharField(max_length=100)
    face_images = models.JSONField(default=list)  # Add this field to store face images

    def __str__(self):
        return self.student_name