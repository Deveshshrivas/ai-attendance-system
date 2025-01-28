from django.test import TestCase
from .models import Attendance

class AttendanceModelTest(TestCase):

    def setUp(self):
        Attendance.objects.create(student_name="John Doe", attendance_date="2023-10-01", status="Present")

    def test_attendance_creation(self):
        attendance = Attendance.objects.get(student_name="John Doe")
        self.assertEqual(attendance.status, "Present")

    def test_attendance_date(self):
        attendance = Attendance.objects.get(student_name="John Doe")
        self.assertEqual(str(attendance.attendance_date), "2023-10-01")