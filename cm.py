from datetime import datetime
import numpy as np
import cv2
import mediapipe as mp

class Squat:
    def __init__(self, reps):
        self.date = datetime.now()
        self.reps = reps
        self.last_direction = None
        self.count = 0 
        self.fast_up = False
        self.fast_d = False
        self.slow_up = True
        self.slow_d = True

    def exsplosive(self):
        """
        discesa 3 sec, salita più veloce possibile
        """
        TIME_SLOW = 5
        TIME_FAST = 1.5
        TIME_FASTD = 0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 135
    
    def endurance(self):
        """
        discesa e salita 4 sec
        """
        TIME_SLOW = 5
        TIME_FAST = 1.5
        TIME_FASTD = 0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 135
    
    def correct_execution(self, image, angle_sx, angle_dx, l_image, a_image):
        """
        apprendimento esercizio
        """
        TIME_SLOW = 5
        TIME_FAST = 1.5
        TIME_FASTD = 0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 135

        try:
            #contatore degli squat e controllo sulle velocità di esecuzione
            #160 è troppo 
            if angle_dx > MAX_ANGLE and angle_sx > MAX_ANGLE:
                #per vedere la velocità del movimento in secondi
                istante_inizio_discesa = datetime.now() 
                self.fast_d = False
                self.slow_d = False 
                if self.last_direction=="up":
                    self.last_direction = "down"
                    self.count+=1
                    #controllo velocità di salita
                    if (datetime.now() - istante_inizio_salita).total_seconds() < TIME_FAST:
                        self.fast_up = True 
                    elif (datetime.now() - istante_inizio_salita).total_seconds() > TIME_SLOW:
                        self.slow_up = True 
                #se stai all'inizio  e su  
                elif self.last_direction==None: 
                    self.last_direction="down"
                    self.count = 0
            elif angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE and self.last_direction=="down":  
                self.last_direction = "up" 
                istante_inizio_salita = datetime.now() 
                self.fast_up = False 
                self.slow_up = False
                #controllo velocità di discesa
                if (datetime.now() - istante_inizio_discesa).total_seconds() < TIME_FASTD:
                    self.fast_d = True
                elif (datetime.now() - istante_inizio_discesa).total_seconds() > TIME_SLOW:
                    self.slow_d = True 
            elif self.last_direction==None:
                self.count=0 

            if self.fast_d or self.fast_up or self.slow_d or self.slow_up:
                #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
                cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 0, 255), -1)
                if self.fast_d:
                    cv2.putText(image, "RALLENTA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                elif self.fast_up:
                    cv2.putText(image, "RALLENTA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                elif self.slow_d:
                    cv2.putText(image, "VELOCIZZA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                else:
                    cv2.putText(image, "VELOCIZZA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
            else:
                #rettangolo verde se esecuzione ok
                cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 255, 0), -1)
                cv2.putText(image, "OK", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))        

            #mostra in alto a sinistra il contatore degli squat in un 
            #rettangolo verde 
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,255,0), -1)
            cv2.putText(image, "Squat :" + str(self.count), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

        except:
            pass

        return image

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
    
    def check_landmarks(self, image, a_image, l_image, landmarks):
        """
        controllo che bacino, ginocchio e cavoglia siano visibili,
        90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
        """
        try: 
            if landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
                #rettangolo rosso che cattura l'attenzione 
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo bacino dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            elif landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo ginocchio dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
            elif landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo caviglia dx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            if landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                #rettangolo rosso che cattura l'attenzione 
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo bacino sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            elif landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
            elif landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                cv2.putText(image, "Non vedo caviglia sx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
        except:
            pass
        return image

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
    squat_counter = Squat(6)
    ui_manager = UIManager(1)

    while ui_manager.cap.isOpened():

        try:
            ret, frame = ui_manager.cap.read()

            landmarks, results = posture_detector.detect_posture(frame)
            frame = posture_detector.check_landmarks(frame, ui_manager.a_image, ui_manager.l_image,landmarks)
            frame = posture_detector.draw_landmarks(frame,results.pose_landmarks)

            asx,adx = posture_detector.calculate_angles(landmarks)

            frame = squat_counter.correct_execution(frame, asx, adx, ui_manager.l_image, ui_manager.a_image)

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
