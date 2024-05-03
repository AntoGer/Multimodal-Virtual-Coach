import mediapipe as mp
import numpy as np
import cv2


class PostureDetector:

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3)

    def calculate_angles(self, landmarks):
        """metodo che calcola angolo gamba"""

        #prende posizione x e y dei 3 joints di dx
        hip_dx = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y])
        knee_dx = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y])
        ankle_dx = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y])

        #prendo posiizione x e y dei joint di sx
        hip_sx = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y])
        knee_sx = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y])
        ankle_sx = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y])
        
        #anca
        #ginocchio
        #caviglia

        radiants_dx = np.arctan2(ankle_dx[1]-knee_dx[1], ankle_dx[0]-knee_dx[0]) - np.arctan2(hip_dx[1]-knee_dx[1], hip_dx[0]-knee_dx[0])
        angle_dx = np.abs(radiants_dx *180.0/np.pi)

        radiants_sx = np.arctan2(ankle_sx[1]-knee_sx[1], ankle_sx[0]-knee_sx[0]) - np.arctan2(hip_sx[1]-knee_sx[1], hip_sx[0]-knee_sx[0])
        angle_sx = np.abs(radiants_sx *180.0/np.pi)

        return angle_sx, angle_dx 
    
    def detect_posture(self, frame):
        try:
            results = self.pose.process(frame)
            landmarks = results.pose_landmarks.landmark
            # Implementa il resto della logica di rilevamento della postura qui
        except:
            pass
        return landmarks, results
    
    def draw_landmarks(self, frame, landmarks):

        try:
            # Render detections
            self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_pose.POSE_CONNECTIONS,
                                    self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        ) 
        except:
            pass
        return frame
    
    
class UIManager:
    def __init__(self,sel_camera):
        self.cap = cv2.VideoCapture(sel_camera)
        self.a_image = self.cap.get(4)
        self.l_image = self.cap.get(3)
        self.mp_drawing = mp.solutions.drawing_utils

    def display_frame(self, frame):
        img_nuova = cv2.resize(frame, (900, 650))
        cv2.imshow("Assistente Fitness", img_nuova)
        cv2.resizeWindow("Assistente Fitness", 900, 650)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
        return True

    def release_capture(self):
        self.cap.release()
        cv2.destroyAllWindows()

def main():
    posture_detector = PostureDetector()
    ui_manager = UIManager(1)

    while ui_manager.cap.isOpened():

        try:
            ret, frame = ui_manager.cap.read()

            landmarks, results = posture_detector.detect_posture(frame)
            #frame = posture_detector.check_landmarks(frame, ui_manager.a_image, ui_manager.l_image,landmarks)
            frame = posture_detector.draw_landmarks(frame,results.pose_landmarks)

            #asx,adx = posture_detector.calculate_angles(landmarks)

            #frame = squat_counter.correct_execution(frame, asx, adx, ui_manager.l_image, ui_manager.a_image)

            # Esegui il conteggio degli squat e visualizza il frame
            # Implementa la logica di conteggio e visualizzazione qui

            ui_manager.display_frame(frame)

            if not ui_manager.display_frame(frame):
                break

        except:
            pass

    ui_manager.release_capture()

if __name__ == "__main__":
    main()
