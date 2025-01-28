
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin_departments/', views.admin_department_list, name='admin_department_list'),
    path('admin_departments/create/', views.admin_department_create, name='admin_department_create'),
    path('admin_departments/<int:pk>/', views.admin_department_detail, name='admin_department_detail'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'), 
    path('register/', views.register, name='register'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('face_recognition_attendance/', views.face_recognition_attendance, name='face_recognition_attendance'),
    path('attendance_success/', views.attendance_success, name='attendance_success'),
    
]