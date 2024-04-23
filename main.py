import cv2
import mediapipe as mp
import numpy as np
#per speech recognition offline, non ancora implementato
import vosk 

def calculate_angles(a, b, c):
    a = np.array(a) #anca
    b = np.array(b) #ginocchio
    c = np.array(c) #caviglia

    radiants = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radiants *180.0/np.pi)

    #questa potresti pure toglierla
    if angle>180:
        angle = 360-angle 
    return angle 

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

#cattura video
cap = cv2.VideoCapture(0) 
counter = 0
f_counter = None 

#Pose in input ha static_image_mode=False perchè input è video stream e non immagine 
#min_detection_confidence è la soglia sopra la quale identifica correttamente un nuovo indivuduo
#min_tracking_confidence è la soglia minima sopra la quale un individuo gia identificato rimane tracciato
with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.45) as pose:
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
        
        #extract landmarks 
        try:
            landmarks = results.pose_landmarks.landmark
            #print(type(landmarks),landmarks) 

            #controllo che bacino, ginocchio e cavoglia siano visibili 
            #90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
            f=False 
            if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
                #rettangolo rosso che cattura l'attenzione 
                cv2.rectangle(image, (0,0), (350, 70), (0,0,255), -1)
                cv2.putText(image, "Non vedo bacino dx",(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                f=True 
            elif landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (380, 70), (0,0,255), -1)
                cv2.putText(image, "Non vedo ginocchio dx",(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                f=True
            elif landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
                cv2.rectangle(image, (0,0), (350, 70), (0,0,255), -1)
                cv2.putText(image, "Non vedo caviglia dx ",(10,30), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                f=True

            if f==True: 
                #ridimensionamento frame e finestra video
                larghezza_nuova = 900
                altezza_nuova = 650
                img_nuova = cv2.resize(image, (larghezza_nuova, altezza_nuova))
                #crea popup con il video
                cv2.imshow('Mediapipe Feed', img_nuova) 
                cv2.resizeWindow("Mediapipe Feed", larghezza_nuova, altezza_nuova)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                continue    
            #prende posizione x e y dei 3 joints
            anca = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
            ginocchio = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
            caviglia = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

            #calcola l'angolo dei 3 punti
            angle = calculate_angles(anca, ginocchio, caviglia)

            #mostra l'angolo calcolato
            cv2.putText(image, str(angle), 
                        tuple(np.multiply(ginocchio,[640, 480]).astype(int)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,255,255), 2, cv2.LINE_AA
                              )
           
            #contatore degli squat
            #160 è troppo 
            if angle > 140:
                f_counter = "down"
            if angle < 60 and f_counter =="down": 
                f_counter = "up" 
                counter +=1
            #print(counter) 

            #mostra in alto a sinistra il contatore degli squat in un 
            #rettangolo verde 
            cv2.rectangle(image, (0,0), (350, 70), (0,255,0), -1)
            cv2.putText(image, "Squat :" + str(counter), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

            #Mostra le visibility di anca, ginocchio e caviglia nel frame
            cv2.putText(image, "anca "+ str(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility),(10,410),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,255,255), 2, cv2.LINE_AA)
            cv2.putText(image, "ginocchio "+ str(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility),(10,440), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,255,255), 2, cv2.LINE_AA)
            cv2.putText(image, "caviglia "+ str(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility),(10,470), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,255,255), 2, cv2.LINE_AA)


        except:
            pass

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
        cv2.imshow('Mediapipe Feed', img_nuova) 
        cv2.resizeWindow("Mediapipe Feed", larghezza_nuova, altezza_nuova)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()