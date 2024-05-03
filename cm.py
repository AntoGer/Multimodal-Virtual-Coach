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
                #rettangolo verde se esecuzione
                cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 255, 0), -1)
                cv2.putText(image, "OK", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))        

            #mostra in alto a sinistra il contatore degli squat in un 
            #rettangolo verde 
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,255,0), -1)
            cv2.putText(image, "Squat :" + str(self.count), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

        except:
            pass

        return image
    
    def back(self, image, angle, anca_sx, landmarks, l_image, a_image):
        try:        
            #mostra l'angolo calcolato
            cv2.putText(image, str(int(angle)), 
                        tuple(np.multiply(anca_sx,[l_image, a_image]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                            )
            
            if (self.last_direction == None or self.last_direction == 'down' and angle < 130) or (self.last_direction == 'up' and angle < 45):
                    cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.75), int(a_image*0.25)), (0, 0, 255), -1)
                    cv2.putText(image, "SCHIENA TROPPO INCLINATA", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

            #Mostra le visibility di spalla, anca e ginocchio sx nel frame laterale
            cv2.putText(image, "spalla sx "+ str(int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            cv2.putText(image, "anca sx "+ str(int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            cv2.putText(image, "ginocchio sx "+ str(int(landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        
        except:
            pass

        return image
    
class PostureDetector:

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3)
        self.knee_point_sx = None
        self.knee_point_dx = None

    def calculate_angles_back(self, landmarks):
        
        #prende posizione x e y dei 3 joints di dx
        spalla_sx = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        anca_sx = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y]
        ginocchio_sx = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y]

        radiants = np.arctan2(ginocchio_sx[1]-anca_sx[1], ginocchio_sx[0]-anca_sx[0]) - np.arctan2(spalla_sx[1]-anca_sx[1], spalla_sx[0]-anca_sx[0])
        angle = np.abs(radiants *180.0/np.pi)

        self.hip_point=anca_sx

        return angle, anca_sx


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

        self.knee_point_dx = knee_dx
        self.knee_point_sx = knee_sx

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
    
    def show_angles(self, frame, angle, point, l_image, a_image):
        
        #mostra l'angolo calcolato
        cv2.putText(frame, str(int(angle)), 
                    tuple(np.multiply(point,[l_image, a_image]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                        )
        
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
        #self.mp_drawing = mp.solutions.drawing_utils

    def display_frame(self, frame):
        img_nuova = cv2.resize(frame, (900, 650))
        cv2.imshow("Assistente Fitness", img_nuova)
        cv2.resizeWindow("Assistente Fitness", 900, 650)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
        return True
    
    def display_double_frame(self, frame, frame_2):
        larghezza_nuova = 900
        altezza_nuova = 650
        #img_nuova = cv2.resize(image, (larghezza_nuova, altezza_nuova))
        img_composta = np.concatenate((cv2.resize(frame, (self.l_image, self.a_image)), cv2.resize(frame_2,(self.l_image, self.a_image))), axis=1) 
        img_nuova = cv2.resize(img_composta, (larghezza_nuova, altezza_nuova))
        #crea popup con il video
        cv2.imshow("Assistente Fitness", img_nuova) 
        cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
        return True
  
    def release_capture(self):
        self.cap.release()

def main():
    posture_detector = PostureDetector()
    posture_detector1 = PostureDetector()
    squat_counter = Squat(6)
    ui_manager_front = UIManager(0)
    ui_manager_2 = UIManager(1)

    while ui_manager_front.cap.isOpened():

        try:
            ret, frame = ui_manager_front.cap.read()
            ret_2, frame_2 = ui_manager_2.cap.read()
            
            landmarks, results = posture_detector.detect_posture(frame)
            frame = posture_detector.check_landmarks(frame, ui_manager_front.a_image, ui_manager_front.l_image,landmarks)
            frame = posture_detector.draw_landmarks(frame,results.pose_landmarks)

            landmarks_2, results_2 = posture_detector1.detect_posture(frame_2)
            frame_2 = posture_detector1.check_landmarks(frame_2, ui_manager_2.a_image, ui_manager_2.l_image,landmarks_2)
            frame_2 = posture_detector1.draw_landmarks(frame_2,results_2.pose_landmarks)
            
            asx,adx = posture_detector.calculate_angles(landmarks)

            frame = posture_detector.show_angles(frame, asx, posture_detector.knee_point_sx, ui_manager_front.l_image, ui_manager_front.a_image)
            frame = posture_detector.show_angles(frame, adx, posture_detector.knee_point_dx, ui_manager_front.l_image, ui_manager_front.a_image)

            frame = squat_counter.correct_execution(frame, asx, adx, ui_manager_front.l_image, ui_manager_front.a_image)
            
            absx, hip_sx = posture_detector1.calculate_angles_back(landmarks_2)

            frame = posture_detector.show_angles(frame, absx, hip_sx, ui_manager_2.l_image, ui_manager_2.a_image)

            frame = squat_counter.back(frame, absx, hip_sx, landmarks_2, ui_manager_2.l_image, ui_manager_2.a_image)

            merged_frame = cv2.hconcat([frame, frame_2])

            if not ui_manager_front.display_frame(merged_frame):
                break

        except:
            pass

    ui_manager_front.release_capture()

if __name__ == "__main__":
    main()
    cv2.destroyAllWindows()