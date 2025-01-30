import cv2
import dlib
import os
import numpy as np
from django.utils.timezone import now
from scipy.spatial import distance
from .models import StudentRegistration, AttendanceRecord

# Get absolute path to model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
shape_predictor_path = os.path.join(BASE_DIR, 'static', 'shape_predictor_68_face_landmarks.dat')
face_rec_model_path = os.path.join(BASE_DIR, 'static', 'dlib_face_recognition_resnet_model_v1.dat')

# Initialize Dlib models 
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)

# Load known faces from student images
known_face_encodings = []
known_face_names = []

def load_student_faces():
    """Loads face encodings of all students from stored images."""
    global known_face_encodings, known_face_names
    known_face_encodings.clear()
    known_face_names.clear()

    students = StudentRegistration.objects.all()
    
    for student in students:
        student_id = student.id
        student_name = student.student_name
        image_folder = os.path.join(BASE_DIR, "media", "students", str(student_id))

        if not os.path.exists(image_folder):
            print(f"No images found for {student_name} ({student_id})")
            continue

        for img_name in os.listdir(image_folder):
            img_path = os.path.join(image_folder, img_name)
            image = cv2.imread(img_path)
            faces = detector(image, 1)

            for face in faces:
                shape = shape_predictor(image, face)
                face_chip = dlib.get_face_chip(image, shape)
                face_encoding = np.array(face_rec_model.compute_face_descriptor(face_chip))

                known_face_encodings.append(face_encoding)
                known_face_names.append((student_id, student_name))

        print(f"Loaded {len(known_face_encodings)} faces for {student_name} ({student_id})")

def mark_attendance(student_id, student_name):
    """Marks attendance if not already marked for today."""
    today = now().date()
    
    if AttendanceRecord.objects.filter(student_Enrollment=student_id, attendance_date=today).exists():
        print(f"Attendance already marked for {student_name} ({student_id})")
        return

    AttendanceRecord.objects.create(
        student_name=student_name,
        student_Enrollment=student_id,
        attendance_date=today,
        status="Present"
    )
    print(f"Attendance marked for {student_name} ({student_id})")

def recognize_faces(ip_cam_url):
    """Recognizes faces in real-time and marks attendance."""
    video_capture = cv2.VideoCapture(ip_cam_url)
    if not video_capture.isOpened():
        print("Failed to open IP camera.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture image")
            break

        faces = detector(frame, 1)
        for face in faces:
            shape = shape_predictor(frame, face)
            face_encoding = np.array(face_rec_model.compute_face_descriptor(frame, shape))

            distances = [distance.euclidean(face_encoding, known_enc) for known_enc in known_face_encodings]
            min_distance = min(distances) if distances else None
            name = "Unknown"

            if min_distance is not None and min_distance < 0.6:  # Face match threshold
                student_id, student_name = known_face_names[distances.index(min_distance)]
                mark_attendance(student_id, student_name)
                name = student_name

            # Draw rectangle and name
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
            cv2.putText(frame, name, (face.left(), face.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Live Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

def start_attendance(ip_cam_url):
    """Loads faces and starts real-time recognition."""
    print("Loading student faces...")
    load_student_faces()
    print("Starting real-time face recognition...")
    recognize_faces(ip_cam_url)
