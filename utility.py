import mediapipe as mp
import cv2
import numpy as np
import speech_recognition as sr
from datetime import datetime
import time 

class speech_interaction:

    def __init__(self, grammar):
        self.vocal_command = False 
        self.recognizer = sr.Recognizer() 
        self.microphone = sr.Microphone(0)
        self.l_grammar = grammar
        #qui si fa calibrazione del microfono per 1 secondo, in modo da distinguere 
        #il rumore dalla voce
        with self.microphone as source:
            print("Silenzio per 1 secondo per calibrazione microfono!") 
            self.recognizer.adjust_for_ambient_noise(source) 
            print("Fatto")

    def check_voice_command(self, recognizer, audio):
        #bisogna creare un dizionario di parole chiavi che interrompono  
        #il programma se pronunciate
        print("in ascolto...")
        try:
            # Riconosce il discorso
            text = recognizer.recognize_google(audio, language='it-IT')
            print("hai detto "+text) 
            for parola in self.l_grammar:
                if parola in text.lower():
                    #print("Esecuzione interrotta dall'input vocale.")
                    # Se la parola chiave è rilevata, imposta una variabile globale per interrompere il ciclo
                    #global stop_vocal_command 
                    self.vocal_command = True
                    print("interruzione per "+text.lower()) 
                    break 
        except sr.UnknownValueError:
            print("Non ho capito.")
        except sr.RequestError as e:
            print(f"Errore nella richiesta al servizio di riconoscimento vocale: {e}")

def draw_rectangle(image, pp , pa , color, thickness, r):
    x, y = pp[0], pp[1]
    w, h = pa[0], pa[1]

    # Disegna i quattro angoli smussati
    cv2.circle(image, (x+r, y+r), r, color, thickness)
    cv2.circle(image, (x+w-r, y+r), r, color, thickness)
    cv2.circle(image, (x+r, y+h-r), r, color, thickness)
    cv2.circle(image, (x+w-r, y+h-r), r, color , thickness)

    # Disegna i quattro lati del rettangolo
    cv2.rectangle(image, (x+r, y), (x+w-r, y+h), color , thickness)
    cv2.rectangle(image, (x, y+r), (x+w, y+h-r), color , thickness) 

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
                        cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, 16
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
                draw_rectangle(image, (int(l_image*0.005), int(a_image*0.005)), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1 , 20)
                #controllo che bacino, ginocchio e caviglia dx e sx siano ben visibili 
                #90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
                if landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
                    cv2.putText(image, "Non vedo bacino dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)
                elif landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo ginocchio dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.9 ,(0,0,0), 2, 16)
                elif landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo caviglia dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                    cv2.putText(image, "Non vedo bacino sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.9 ,(0,0,0), 2, 16)
                elif landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:
                    cv2.putText(image, "Non vedo caviglia sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)

        else:
            if landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8 or landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8: 
                    f_errore = True
                    #rettangolo rosso che cattura l'attenzione  
                    draw_rectangle(image, (int(l_image*0.005), int(a_image*0.005)), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1 , 20)
                    #controlli di visibilità dei joints cruciali
                    if landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8:
                        cv2.putText(image, "Non vedo spalla sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)
                    elif landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                        cv2.putText(image, "Non vedo anca sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, 16)
                    elif landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.9 ,(0,0,0), 2, 16)

        return image, f_errore

class UIManager:
    def __init__(self,sel_camera):
        #False quando mostro la schermata finale con riassunto degli
        #squat fatti
        #if sel_camera != "no":
        self.cap = cv2.VideoCapture(sel_camera)
        self.a_image = int(self.cap.get(4)) 
        self.l_image = int(self.cap.get(3)) 
        self.larghezza_nuova = 1300
        self.altezza_nuova = 850

    def display_final_frame_squat(self, n_squat, tempo):
        if n_squat > 0:
            #np.full altezza, larghezza (prima Y e poi la X)
            img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,255,0), dtype =np.uint8)
            #putText larghezza, altezza (prima X e poi Y)
            cv2.putText(img_finale, "Hai completato "+str(n_squat)+" squat in "+ str(tempo)+ " secondi!", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.4)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)  
        else: 
            img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,0,255), dtype =np.uint8)
            cv2.putText(img_finale, "Hai completato 0 squat in "+ str(tempo)+ " secondi!", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.4)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)
        while True:
            cv2.imshow("Assistente Fitness", img_finale)
            cv2.resizeWindow("Assistente Fitness", self.larghezza_nuova, self.altezza_nuova)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
    
    def display_final_frame_wallsit(self, durata_reale_sec, sec_persi, iniziato):
        if sec_persi == 0:
            if not(iniziato): 
                #allora non hai mai iniziato, non sei mai stato in posizione corretta
                img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,0,255), dtype =np.uint8) 
                cv2.putText(img_finale, "Non hai mai iniziato !", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)
            else:
                img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,255 ,0), dtype =np.uint8) 
                cv2.putText(img_finale, "Esecuzione perfetta !", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)
        elif sec_persi/durata_reale_sec < 0.3: 
            img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,255,0), dtype =np.uint8) 
            cv2.putText(img_finale, "Hai sbagliato per soli "+str(round(sec_persi, 1) )+" secondi su "+ str(durata_reale_sec) +" totali !", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)  
        else:
            img_finale = np.full((self.altezza_nuova, self.larghezza_nuova, 3),(0,0,255), dtype =np.uint8) 
            cv2.putText(img_finale, "Devi migliorare! Hai sbagliato per "+str(round(sec_persi, 1) )+" secondi su "+ str(durata_reale_sec) +" totali !", (int(self.larghezza_nuova*0.25), int(self.altezza_nuova*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2, 16)  
        while True:
            cv2.imshow("Assistente Fitness", img_finale)
            cv2.resizeWindow("Assistente Fitness", self.larghezza_nuova, self.altezza_nuova)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 

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

    ui_manager_front = UIManager(0)

    #GOOGLE API 
    #serve per capire quando terminare il programma
    vcom_stop = speech_interaction(["stop", "ferma", "termina"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)

    while ui_manager_front.cap.isOpened() and not vcom_stop.vocal_command :
        
        ret, frame = ui_manager_front.cap.read()

        ui_manager_front.display_frame(frame)

        if vcom_stop.vocal_command == True:
            print("si")

    #GOOGLE API         
    stop_listening(wait_for_stop = False)

    ui_manager_front.release_capture()
    cv2.destroyAllWindows()