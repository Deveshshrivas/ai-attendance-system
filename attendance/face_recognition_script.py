import cv2
import dlib
import os
import numpy as np
from dotenv import load_dotenv
from scipy.spatial import distance
from .models import StudentRegistration

# Load environment variables from .env file
load_dotenv()

# Get the absolute path to the model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
shape_predictor_path = os.path.join(BASE_DIR, 'static', 'shape_predictor_68_face_landmarks.dat')
face_rec_model_path = os.path.join(BASE_DIR, 'static', 'dlib_face_recognition_resnet_model_v1.dat')

# Initialize Dlib models 
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)

# In-memory storage for known faces
known_face_encodings = []
known_face_names = []

def load_known_faces():
    """Fetch all student IDs and load their face images from the directory."""
    students = StudentRegistration.objects.all()
    
    for student in students:
        student_id = student.id
        student_name = student.student_name
        student_dir = os.path.join(BASE_DIR, 'media', 'student', str(student_id))

        if os.path.exists(student_dir):
            for file in os.listdir(student_dir):
                image_path = os.path.join(student_dir, file)

                if image_path.endswith(('.jpg', '.jpeg', '.png')):  # Ensure it's an image
                    image = cv2.imread(image_path)
                    faces = detector(image, 1)
                    if len(faces) > 0:
                        for face in faces:
                            shape = shape_predictor(image, face)
                            face_chip = dlib.get_face_chip(image, shape)
                            face_encoding = np.array(face_rec_model.compute_face_descriptor(face_chip))
                            known_face_encodings.append(face_encoding)
                            known_face_names.append(student_name)
                            print(f"✅ Loaded face encoding for {student_name} from {file}")
                    else:
                        print(f"⚠️ No face detected in {image_path}")
        else:
            print(f"🚫 No images found for student ID {student_id}")

def recognize_faces(ip_cam_url):
    """Recognize faces from a live camera feed using known encodings."""
    video_capture = cv2.VideoCapture(ip_cam_url)
    if not video_capture.isOpened():
        print("⚠️ Failed to open IP camera.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("⚠️ Failed to capture image")
            break

        # Detect faces in the frame
        faces = detector(frame, 1)
        for face in faces:
            shape = shape_predictor(frame, face)
            face_encoding = np.array(face_rec_model.compute_face_descriptor(frame, shape))

            # Match the face encoding with known faces
            distances = [distance.euclidean(face_encoding, known_enc) for known_enc in known_face_encodings]
            min_distance = min(distances) if distances else None
            name = "Unknown"

            if min_distance is not None and min_distance < 0.65:  # Adjusted threshold
                name = known_face_names[distances.index(min_distance)]

            # Draw a rectangle around the face
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
            cv2.putText(frame, name, (face.left(), face.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Load known faces once at the start
load_known_faces()
