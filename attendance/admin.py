from django.contrib import admin
from .models import CustomUser, AdminDepartment, Attendance, TeacherRegistration, StudentRegistration

# Register your models here
admin.site.register(CustomUser)
admin.site.register(AdminDepartment)
admin.site.register(Attendance)
admin.site.register(TeacherRegistration)
admin.site.register(StudentRegistration)