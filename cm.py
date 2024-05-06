from datetime import datetime
import numpy as np
import cv2
import mediapipe as mp

class Squat:
    def __init__(self, reps):
        self.starting_instant = datetime.now()
        self.reps = reps
        self.current_direction = None
        self.count = 0 
        self.fast_up = False
        self.fast_d = False
        self.slow_up = True
        self.slow_d = True
        self.current_position = None
        self.istante_inizio_discesa = datetime.now() 
        self.istante_inizio_salita = datetime.now()

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
    
    def correct_execution(self, image, angle_sx, angle_dx, l_image, a_image, mp_pose):
        """
        apprendimento esercizio da parte dell'utente
        """
        TIME_SLOW = 5
        TIME_FAST = 1.5
        TIME_FASTD = 0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 60 #135

        #contatore degli squat e controllo sulle velocità di esecuzione
        #160 è troppo 
        if angle_dx > MAX_ANGLE and angle_sx > MAX_ANGLE:
            #serve per capire quale angolo della schiena controllare
            self.current_position = "up"
            #per vedere la velocità del movimento in secondi
            self.istante_inizio_discesa = datetime.now() 
            self.fast_d = False
            self.slow_d = False 
            if self.current_direction == "up":
                self.current_direction = "down"
                self.count+=1
                #controllo velocità di salita
                if (datetime.now() - self.istante_inizio_salita).total_seconds() < TIME_FAST:
                    self.fast_up = True 
                elif (datetime.now() - self.istante_inizio_salita).total_seconds() > TIME_SLOW:
                    self.slow_up = True 
            #se stai all'inizio  e su  
            elif self.current_direction == None: 
                self.current_direction = "down"
                #perchè si inizia quando si sta su e si scende, e non quando si instanzia 
                #l'oggetto squat
                self.starting_instant = max(self.starting_instant,datetime.now()) 
                self.count = 0
        elif angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE and self.current_direction == "down":  
            #serve per capire quale angolo della schiena controllare
            self.current_position = "down"
            self.current_direction = "up" 
            self.istante_inizio_salita = datetime.now() 
            self.fast_up = False 
            self.slow_up = False
            #controllo velocità di discesa
            if (datetime.now() - self.istante_inizio_discesa).total_seconds() < TIME_FASTD:
                self.fast_d = True
            elif (datetime.now() - self.istante_inizio_discesa).total_seconds() > TIME_SLOW:
                self.slow_d = True 
        elif self.current_direction == None:
            self.count = 0 

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
        

        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
        cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
        cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
        
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        
        #il secondo argomento calcola il tempo passato dall'inizio del 1 squat
        return image, round((datetime.now() - self.starting_instant).total_seconds(),1) 
    
    
    def back(self, image, angle_back, landmarks, l_image, a_image, mp_pose):
        ANGLE_BACK_UP = 130
        ANGLE_BACK_DOWN = 30

        if (self.current_position == "up" and  angle_back < ANGLE_BACK_UP) or (self.current_position == "down" and  angle_back < ANGLE_BACK_DOWN):
            cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.75), int(a_image*0.25)), (0, 0, 255), -1)
            cv2.putText(image, "SCHIENA TROPPO INCLINATA", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

        #Mostra le visibility di spalla, anca e ginocchio sx nel frame laterale
        cv2.putText(image, "spalla sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
    
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

        if angle > 180:
            angle = 360-angle 

        self.hip_point = anca_sx

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

        if angle_dx > 180:
            angle_dx = 360-angle_dx 
        
        if angle_sx > 180:
            angle_sx = 360-angle_sx 

        self.knee_point_dx = knee_dx
        self.knee_point_sx = knee_sx

        return angle_sx, angle_dx 
    
    def detect_posture(self, frame):
        #conversione in RGB perchè process vuole RGB e non BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
        results = self.pose.process(frame) 
        frame.flags.writeable = True 
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        landmarks = results.pose_landmarks.landmark 
        # Implementa il resto della logica di rilevamento della postura qui    
        return landmarks, results
    
    def draw_landmarks(self, frame, landmarks):
        # Render detections
        self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_pose.POSE_CONNECTIONS,
                                    self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        ) 
        return frame
    
    def show_angles(self, frame, angle, point, l_image, a_image):
        
        #mostra l'angolo calcolato
        cv2.putText(frame, str(int(angle)), 
                    tuple(np.multiply(point,[l_image, a_image]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                        )
        
        return frame
    
    def check_landmarks(self, image, l_image, a_image, landmarks, cam = 0):
        """
        controllo che bacino, ginocchio e cavoglia siano visibili,
        90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
        """
        f_errore = False
        #controllo alcuni joints se guardo da davanti(0) e altri se guardo da di fianco(1)
        if cam == 0: 
            if landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:#f == True: 
                f_errore = True
                #rettangolo rosso che cattura l'attenzione 
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                #controllo che bacino, ginocchio e caviglia dx e sx siano ben visibili 
                #90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
                if landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
                    cv2.putText(image, "Non vedo bacino dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                elif landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo ginocchio dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                elif landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo caviglia dx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                    cv2.putText(image, "Non vedo bacino sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo caviglia sx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)

        else:
            if landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8: 
                    f_errore = True
                    #rettangolo rosso che cattura l'attenzione 
                    cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1) 
                    #controlli di visibilità dei joints cruciali
                    if landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8:
                        cv2.putText(image, "Non vedo spalla sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                        cv2.putText(image, "Non vedo anca sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)

        return image, f_errore

class UIManager:
    def __init__(self,sel_camera):
        self.cap = cv2.VideoCapture(sel_camera)
        self.a_image = int(self.cap.get(4))
        self.l_image = int(self.cap.get(3)) 
        self.larghezza_nuova = 900
        self.altezza_nuova = 650
        #self.mp_drawing = mp.solutions.drawing_utils

    def display_frame(self, frame):
        img_nuova = cv2.resize(frame, (self.larghezza_nuova, self.altezza_nuova))
        cv2.imshow("Assistente Fitness", img_nuova)
        cv2.resizeWindow("Assistente Fitness", self.larghezza_nuova, self.altezza_nuova)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
        return True
    
    def display_double_frame(self, frame, frame_2):
        img_composta = np.concatenate((cv2.resize(frame, (self.l_image, self.a_image)), cv2.resize(frame_2,(self.l_image, self.a_image))), axis=1) 
        img_nuova = cv2.resize(img_composta, (self.larghezza_nuova, self.altezza_nuova))
        #crea popup con il video
        cv2.imshow("Assistente Fitness", img_nuova) 
        cv2.resizeWindow("Assistente Fitness", self.larghezza_nuova, self.altezza_nuova)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
        return True
  
    def release_capture(self):
        self.cap.release()

if __name__ == "__main__":
    posture_detector = PostureDetector()
    posture_detector1 = PostureDetector()
    squat_counter = Squat(6)
    ui_manager_front = UIManager(0)
    ui_manager_1 = UIManager(1)

    while ui_manager_front.cap.isOpened():

        ret, frame = ui_manager_front.cap.read()
        ret_1, frame_1 = ui_manager_1.cap.read()
        try:
            #estraggo landmark, controllo visibilità e li mostro (webcam avanti)
            landmarks, results = posture_detector.detect_posture(frame)
            #print(landmarks)
        except:
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            if not ui_manager_front.display_frame(merged_frame):
                break
            continue 

        #questo non da errori neanche se non ci sono landmark
        frame, errore = posture_detector.check_landmarks(frame, ui_manager_front.l_image, ui_manager_front.a_image, landmarks, 0)
        if errore:
            merged_frame = cv2.hconcat([frame, frame_1])
            if not ui_manager_front.display_frame(merged_frame):
                break 
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame = posture_detector.draw_landmarks(frame, results.pose_landmarks)
        

        #estraggo landmark e li mostro (camera laterale)
        try:
            landmarks_1, results_1 = posture_detector1.detect_posture(frame_1)
        except :
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            if not ui_manager_front.display_frame(merged_frame):
                break
            continue 

        #controllo visibilità landmark camera laterale 
        frame_1, errore_1 = posture_detector1.check_landmarks(frame_1, ui_manager_1.l_image, ui_manager_1.a_image, landmarks_1, 1)
        if errore_1:
            merged_frame = cv2.hconcat([frame, frame_1])
            if not ui_manager_front.display_frame(merged_frame):
                break 
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame_1 = posture_detector1.draw_landmarks(frame_1, results_1.pose_landmarks)
        
        #calcolo angoli, li mostra e controllo corretta esecuzione (webcam avanti)
        asx, adx = posture_detector.calculate_angles(landmarks)
        frame = posture_detector.show_angles(frame, asx, posture_detector.knee_point_sx, ui_manager_front.l_image, ui_manager_front.a_image)
        frame = posture_detector.show_angles(frame, adx, posture_detector.knee_point_dx, ui_manager_front.l_image, ui_manager_front.a_image)
        frame, tempo_sec = squat_counter.correct_execution(frame, asx, adx, ui_manager_front.l_image, ui_manager_front.a_image, posture_detector.mp_pose)
        
        #calcola angoli, li mostra e controllo agolazione schiena (camera laterale)
        absx, hip_sx = posture_detector1.calculate_angles_back(landmarks_1)
        frame_1 = posture_detector.show_angles(frame_1, absx, hip_sx, ui_manager_1.l_image, ui_manager_1.a_image)
        frame_1 = squat_counter.back(frame_1, absx, landmarks_1, ui_manager_1.l_image, ui_manager_1.a_image, posture_detector.mp_pose)
        
        merged_frame = cv2.hconcat([frame, frame_1])

        cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.01)) , (int(ui_manager_front.larghezza_nuova*0.6), int(ui_manager_front.altezza_nuova*0.1)), (255, 255, 255), -1)
        cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.48), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
    

        if not ui_manager_front.display_frame(merged_frame):
            break


    ui_manager_front.release_capture()
    ui_manager_1.release_capture() 
    cv2.destroyAllWindows()