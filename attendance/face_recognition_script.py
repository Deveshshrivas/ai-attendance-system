import cv2
import dlib
import os
import numpy as np
from dotenv import load_dotenv
from scipy.spatial import distance

# Load environment variables from .env file
load_dotenv()

# Get the absolute path to the model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
shape_predictor_path = os.path.join(BASE_DIR, 'static','shape_predictor_68_face_landmarks.dat', 'shape_predictor_68_face_landmarks.dat')
face_rec_model_path = os.path.join(BASE_DIR, 'static','dlib_face_recognition_resnet_model_v1.dat', 'dlib_face_recognition_resnet_model_v1.dat')

# Initialize Dlib models 
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(shape_predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)

# In-memory storage for known faces 
known_face_encodings = []
known_face_names = []

def capture_images(name, ip_cam_url, num_samples=20):
    video_capture = cv2.VideoCapture(ip_cam_url)
    if not video_capture.isOpened():
        print("Failed to open IP camera.")
        return

    count = 0
    while count < num_samples:
        ret, frame = video_capture.read()
        if ret:
            # Detect faces
            faces = detector(frame, 1)
            if len(faces) > 0:
                for face in faces:
                    # Align face using landmarks
                    shape = shape_predictor(frame, face)
                    face_chip = dlib.get_face_chip(frame, shape)

                    # Encode face and store in memory
                    face_encoding = np.array(face_rec_model.compute_face_descriptor(face_chip))
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(name)

                    print(f"Image {count + 1} captured and encoded")
                    cv2.imshow("Captured Image", face_chip)
                    cv2.waitKey(500)  # Wait before capturing the next image
                    count += 1

                    if count == 10:
                        print("Please turn your face to the left.")
                    elif count == 15:
                        print("Please turn your face to the right.")
            else:
                print("No face detected.")
        else:
            print("Failed to capture image")
            break

    video_capture.release()
    cv2.destroyAllWindows()

def recognize_faces(ip_cam_url):
    video_capture = cv2.VideoCapture(ip_cam_url)
    if not video_capture.isOpened():
        print("Failed to open IP camera.")
        return

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture image")
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

            if min_distance is not None and min_distance < 0.6:  # Adjust threshold as needed
                name = known_face_names[distances.index(min_distance)]

            # Draw a rectangle around the face
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
            cv2.putText(frame, name, (face.left(), face.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

def run_face_recognition():
    # Example of running the face recognition functions 
    ip_cam_url = input("Enter the IP camera URL: ")
    person_name = input("Enter the name of the person to capture: ")
    capture_images(person_name, ip_cam_url)
    recognize_faces(ip_cam_url)
