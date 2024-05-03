import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
#per speech recognition offline, non ancora implementato
#import vosk 

def calculate_angles(hip, knee, ankle):
    hip = np.array(hip) #anca
    knee = np.array(knee) #ginocchio
    ankle = np.array(ankle) #caviglia

    radiants = np.arctan2(ankle[1]-knee[1], ankle[0]-knee[0]) - np.arctan2(hip[1]-knee[1], hip[0]-knee[0])
    angle = np.abs(radiants *180.0/np.pi)

    #questa potresti pure toglierla
    #if angle>180:
        #angle = 360-angle 
    return angle 

def check_landmarks(image, a_image, l_image, landmarks):
    """
    controllo che bacino, ginocchio e cavoglia siano visibili,
    90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
    """
    try:
        f=False 
        if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
            #rettangolo rosso che cattura l'attenzione 
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo bacino dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            f=True 
        elif landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo ginocchio dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
            f=True
        elif landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo caviglia dx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            f=True
        if landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
            #rettangolo rosso che cattura l'attenzione 
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo bacino sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            f=True 
        elif landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
            f=True
        elif landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:
            cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
            cv2.putText(image, "Non vedo caviglia sx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
            f=True
        """ 
        if f==True: 
            #ridimensionamento frame e finestra video
            larghezza_nuova = 900
            altezza_nuova = 650
            img_nuova = cv2.resize(image, (larghezza_nuova, altezza_nuova))
            #crea popup con il video
            cv2.imshow("Assistente Fitness", img_nuova) 
            cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova) 
        """
    except:
        print("unable to check landmarks")

counter_squat = -1
#fast_counter_squat = 0q
#slow_counter_squat = 0
f_direzione = None 

def squat(image, f_direzione, a_image, l_image, angle_dx, angle_sx, counter_squat):

    #contatore squat e flag per vedere se in salita o in discesa
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
            f_discesa_veloce = False
            f_discesa_lenta = False 
            if f_direzione=="up":
                f_direzione = "down"
                counter_squat+=1
                #controllo velocità di salita
                if (datetime.now() - istante_inizio_salita).total_seconds() < TIME_FAST:
                    f_salita_veloce = True 
                elif (datetime.now() - istante_inizio_salita).total_seconds() > TIME_SLOW:
                    f_salita_lenta = True 
            #se stai all'inizio  e su  
            elif f_direzione==None: 
                f_direzione="down"
                counter_squat = 0
        elif angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE and f_direzione=="down":  
            f_direzione = "up" 
            istante_inizio_salita = datetime.now() 
            f_salita_veloce = False 
            f_salita_lenta = False
            #controllo velocità di discesa
            if (datetime.now() - istante_inizio_discesa).total_seconds() < TIME_FASTD:
                f_discesa_veloce = True
            elif (datetime.now() - istante_inizio_discesa).total_seconds() > TIME_SLOW:
                f_discesa_lenta = True 
        elif f_direzione==None:
            counter_squat=0 

        if f_discesa_veloce or f_salita_veloce or f_discesa_lenta or f_salita_lenta:
            #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
            cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 0, 255), -1)
            if f_discesa_veloce:
                cv2.putText(image, "RALLENTA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
            elif f_salita_veloce:
                cv2.putText(image, "RALLENTA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
            elif f_discesa_lenta:
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
        cv2.putText(image, "Squat :" + str(counter_squat), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

    except:
        pass

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

#cattura video webcam e camera
#0 o 1 webcam,telefono 
cap = cv2.VideoCapture(0) 

dire=0
cs=0

#Pose in input ha static_image_mode=False perchè input è video stream e non immagine 
with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3) as pose:
    """
    model_complexity: 1 full
    min_detection_confidence: soglia sopra la quale identifica correttamente un nuovo indivuduo
    min_tracking_confidence: soglia minima sopra la quale un individuo gia identificato rimane tracciato
    """
    while cap.isOpened():

        ret, frame = cap.read()
        
        #cv2 cattura frame in BGR e non RGB
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
        #print(type(results.pose_landmarks), results.pose_landmarks)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        #altezza e larghezza del frame (480 x 640 la webcam)
        a_image = cap.get(4)#480 len(image) 
        l_image = cap.get(3)#640 len(image[0])
        #extract landmarks 
        try:
            landmarks = results.pose_landmarks.landmark
            #print(type(landmarks),landmarks)

            check_landmarks(image, a_image, l_image, landmarks)

            #prende posizione x e y dei 3 joints di dx
            hip_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
            knee_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
            ankle_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

            #prendo posiizione x e y dei joint di sx
            hip_sx = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
            knee_sx = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
            ankle_sx = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
            #calcola l'angolo dei 3 punti
            angle_dx = calculate_angles(hip_dx, knee_dx, ankle_dx)
            angle_sx = calculate_angles(hip_sx, knee_sx, ankle_sx)

            #contatore squat e flag per vedere se in salita o in discesa
            TIME_SLOW = 5
            TIME_FAST = 1.5
            TIME_FASTD = 0.5
            MAX_ANGLE = 140
            MIN_ANGLE = 135
            
            #contatore degli squat e controllo sulle velocità di esecuzione
            #160 è troppo 
            if angle_dx > MAX_ANGLE and angle_sx > MAX_ANGLE:
                #per vedere la velocità del movimento in secondi
                istante_inizio_discesa = datetime.now() 
                f_discesa_veloce = False
                f_discesa_lenta = False 
                if f_direzione=="up":
                    f_direzione = "down"
                    counter_squat+=1
                    #controllo velocità di salita
                    if (datetime.now() - istante_inizio_salita).total_seconds() < TIME_FAST:
                        f_salita_veloce = True 
                    elif (datetime.now() - istante_inizio_salita).total_seconds() > TIME_SLOW:
                        f_salita_lenta = True 
                #se stai all'inizio  e su  
                elif f_direzione==None: 
                    f_direzione="down"
                    counter_squat = 0
            elif angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE and f_direzione=="down":  
                f_direzione = "up" 
                istante_inizio_salita = datetime.now() 
                f_salita_veloce = False 
                f_salita_lenta = False
                #controllo velocità di discesa
                if (datetime.now() - istante_inizio_discesa).total_seconds() < TIME_FASTD:
                    f_discesa_veloce = True
                elif (datetime.now() - istante_inizio_discesa).total_seconds() > TIME_SLOW:
                    f_discesa_lenta = True 
            elif f_direzione==None:
                counter_squat=0 

            if f_discesa_veloce or f_salita_veloce or f_discesa_lenta or f_salita_lenta:
                #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
                cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 0, 255), -1)
                if f_discesa_veloce:
                    cv2.putText(image, "RALLENTA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                elif f_salita_veloce:
                    cv2.putText(image, "RALLENTA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                elif f_discesa_lenta:
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
            cv2.putText(image, "Squat :" + str(counter_squat), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

            #mostra l'angolo calcolato
            cv2.putText(image, str(int(angle_dx)), 
                        tuple(np.multiply(knee_dx,[l_image, a_image]).astype(int)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                              )
            cv2.putText(image, str(int(angle_sx)), 
                        tuple(np.multiply(knee_sx,[l_image, a_image]).astype(int)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 2 ,(0,140,255), 2, cv2.LINE_AA
                              ) 

            #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
            cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
            cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
            cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
            
            #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
            cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            
            
        except:
            pass
        
        
        if f_direzione!= dire:
            dire=f_direzione
            print(f_direzione)
            print(counter_squat)
            
        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    ) 
        
        #ridimensionamento frame e finestra video
        larghezza_nuova = 900
        altezza_nuova = 650
        img_nuova = cv2.resize(image, (larghezza_nuova, altezza_nuova))
        #crea popup con il video
        cv2.imshow("Assistente Fitness", img_nuova) 
        cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        continue

cap.release()
cv2.destroyAllWindows()


        