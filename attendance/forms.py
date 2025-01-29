from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, StudentRegistration, TeacherRegistration, AdminDepartment

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'is_student', 'is_teacher')

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentRegistration
        fields = ['department_id', 'department_code', 'student_Enrollment', 'student_name', 'student_email', 'student_phone', 'student_address']

class TeacherRegistrationForm(forms.ModelForm):
    class Meta:
        model = TeacherRegistration
        fields = ['department_id', 'department_code', 'teacher_name', 'teacher_email', 'teacher_phone', 'teacher_address']

class AdminDepartmentForm(forms.ModelForm):
    class Meta:
        model = AdminDepartment
        fields = ['department_name', 'department_code', 'department_description', 'department_head', 'password']
