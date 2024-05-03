import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
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

#cattura video webcam e camera 
cap = cv2.VideoCapture(0) 
cap_schiena = cv2.VideoCapture(1) # wifi casa :"http://192.168.178.44:8080/video"   hotspot telefono :"http://192.168.84.218:8080/video" #192.168.178.44:4747/video
#contatore squat e flag per vedere se in salita o in discesa
counter = -1
counter_lenti = 0
counter_veloci = 0
f_direzione = None 
t_tot = 0
#ridimensionamento frame e finestra video
larghezza_nuova = 1000 #900 
altezza_nuova = 750 #650
#Pose in input ha static_image_mode=False perchè input è video stream e non immagine 
#min_detection_confidence è la soglia sopra la quale identifica correttamente un nuovo indivuduo
#min_tracking_confidence è la soglia minima sopra la quale un individuo gia identificato rimane tracciato
with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3) as pose:
    with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.3) as pose_schiena:
        while cap.isOpened():
            #per mostrare il tempo trascorso dal primo squat
            if t_tot != 0:
                t_tot = round((datetime.now() - istante_inizio).total_seconds(),1) 
            ret, frame = cap.read() 
            #cv2 cattura frame in BGR e non RGB
            # Recolor image to RGB 
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            # Make detection
            results = pose.process(image)
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            #altezza e larghezza del frame (480 x 640 la webcam)
            a_image = int(cap.get(4))#480 len(image) 
            l_image = int(cap.get(3))#640 len(image[0])

            #INIZIO PARTE SCHIENA LATERALE--------------------------------------------------------------------
            ret, frame_schiena = cap_schiena.read() 
            image_schiena = cv2.cvtColor(frame_schiena, cv2.COLOR_BGR2RGB)
            image_schiena.flags.writeable = False
            # Make detection
            results_schiena = pose_schiena.process(image_schiena)
            image_schiena.flags.writeable = True
            image_schiena = cv2.cvtColor(image_schiena, cv2.COLOR_RGB2BGR)
            #altezza e larghezza del frame (480 x 640 la webcam)
            a_image_schiena = int(cap_schiena.get(4))#480 len(image) 
            l_image_schiena = int(cap_schiena.get(3))#640 len(image[0])

            f_landmark_schiena = False
            #extract landmarks 
            try:
                landmarks_schiena = results_schiena.pose_landmarks.landmark
                #se qualche joints non è ben visibile allora lo segnalo e vado al prossimo frame 
                if landmarks_schiena[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8 or landmarks_schiena[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8 or landmarks_schiena[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8: 
                    #rettangolo rosso che cattura l'attenzione 
                    cv2.rectangle(image_schiena, (0,0), (int(l_image_schiena*0.55), int(a_image_schiena*0.125)), (0,0,255), -1) 
                    #controlli di visibilità dei joints cruciali
                    if landmarks_schiena[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility <= 0.8:
                        cv2.putText(image_schiena, "Non vedo spalla sx",(int(l_image_schiena*0.015), int(a_image_schiena*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks_schiena[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                        cv2.putText(image_schiena, "Non vedo anca sx",(int(l_image_schiena*0.015), int(a_image_schiena*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks_schiena[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                        cv2.putText(image_schiena, "Non vedo ginocchio sx",(int(l_image_schiena*0.015), int(a_image_schiena*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
            
                    #rettangolo rosso che cattura l'attenzione 
                    img_composta = np.concatenate((image, cv2.resize(image_schiena,(l_image, a_image))), axis=1) 
                    img_nuova = cv2.resize(img_composta, (larghezza_nuova, altezza_nuova))
                    #mostro tempo trascorso in alto al centro 
                    cv2.rectangle(img_nuova, (int(larghezza_nuova*0.8),int(altezza_nuova*0.01)) , (int(larghezza_nuova*0.98), int(altezza_nuova*0.1)), (255, 255, 255), -1)
                    cv2.putText(img_nuova, str(t_tot), (int(larghezza_nuova*0.82), int(altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                    #crea popup con il video
                    cv2.imshow("Assistente Fitness", img_nuova) 
                    cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova)
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break
                    continue    
                #prende posizione x e y dei 3 joints di dx
                spalla_sx_schiena = [landmarks_schiena[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks_schiena[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                anca_sx_schiena = [landmarks_schiena[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks_schiena[mp_pose.PoseLandmark.LEFT_HIP].y]
                ginocchio_sx_schiena = [landmarks_schiena[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks_schiena[mp_pose.PoseLandmark.LEFT_KNEE].y]
                angle_schiena = calculate_angles(spalla_sx_schiena, anca_sx_schiena, ginocchio_sx_schiena)
                f_landmark_schiena = True
                #mostra l'angolo calcolato
                cv2.putText(image_schiena, str(int(angle_schiena)), 
                            tuple(np.multiply(anca_sx_schiena,[l_image_schiena, a_image_schiena]).astype(int)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                                )
                #schiena sotto i 50° è troppo inclinata
                #mostro i landmark della camera laterale
                mp_drawing.draw_landmarks(image_schiena, results_schiena.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    ) 
                #Mostra le visibility di spalla, anca e ginocchio sx nel frame laterale
                cv2.putText(image_schiena, "spalla sx "+ str(int(landmarks_schiena[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility*100)),(int(l_image_schiena*0.55),int(a_image_schiena*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
                cv2.putText(image_schiena, "anca sx "+ str(int(landmarks_schiena[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image_schiena*0.55),int(a_image_schiena*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
                cv2.putText(image_schiena, "ginocchio sx "+ str(int(landmarks_schiena[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image_schiena*0.55),int(a_image_schiena*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
            except:
                #eccezione quando il modello non vede alcun landmark
                pass 
            #FINE PARTE SCHIENA LATERALE--------------------------------------------------------------------

            try:
                landmarks = results.pose_landmarks.landmark
                #se no vede bene qualche landmark fondamentale     
                if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8 or landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8 or landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8 or landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8 or landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8 or landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:#f == True: 
                    #rettangolo rosso che cattura l'attenzione 
                    cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,0,255), -1)
                    #controllo che bacino, ginocchio e caviglia dx e sx siano ben visibili 
                    #90% è troppo alta e non si attiva quasi mai, 80% giusto compromesso
                    if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.8:
                        cv2.putText(image, "Non vedo bacino dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo ginocchio dx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo caviglia dx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.8:
                        cv2.putText(image, "Non vedo bacino sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo ginocchio sx",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,(0,0,0), 2, cv2.LINE_AA)
                    elif landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.8:
                        cv2.putText(image, "Non vedo caviglia sx ",(int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,0,0), 2, cv2.LINE_AA)
                
                    img_composta = np.concatenate((image, cv2.resize(image_schiena,(l_image, a_image))), axis=1) 
                    img_nuova = cv2.resize(img_composta, (larghezza_nuova, altezza_nuova))
                     #mostro tempo trascorso in alto al centro 
                    cv2.rectangle(img_nuova, (int(larghezza_nuova*0.80),int(altezza_nuova*0.01)) , (int(larghezza_nuova*0.98), int(altezza_nuova*0.1)), (255, 255, 255), -1)
                    cv2.putText(img_nuova, str(t_tot), (int(larghezza_nuova*0.82), int(altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                    #crea popup con il video
                    cv2.imshow("Assistente Fitness", img_nuova) 
                    cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova)
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break
                    continue    
                #prende posizione x e y dei 3 joints di dx
                anca_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
                ginocchio_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
                caviglia_dx = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

                #prendo posiizione x e y dei joint di sx
                anca_sx = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
                ginocchio_sx = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
                caviglia_sx = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

                #calcola l'angolo dei 3 punti
                angle_dx = calculate_angles(anca_dx, ginocchio_dx, caviglia_dx)
                angle_sx = calculate_angles(anca_sx, ginocchio_sx, caviglia_sx)

                #mostra l'angolo calcolato
                cv2.putText(image, str(int(angle_dx)), 
                            tuple(np.multiply(ginocchio_dx,[l_image, a_image]).astype(int)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2 ,(255,144,30), 2, cv2.LINE_AA
                                )
                cv2.putText(image, str(int(angle_sx)), 
                            tuple(np.multiply(ginocchio_sx,[l_image, a_image]).astype(int)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 2 ,(0,140,255), 2, cv2.LINE_AA
                                )
                #mostro landmark identificati da webcam anteriore
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    ) 
                
                #contatore degli squat e controllo sulle velocità di esecuzione
                #160 è troppo 
                if f_landmark_schiena: #controllo solo quando ho i landmark webcam e laterali
                    if angle_dx > 140 and angle_sx > 140 : 
                        #controllo inclinazione schiena
                        if angle_schiena > 130:
                            f_schiena_troppo_inclinata = False 
                        else:
                            f_schiena_troppo_inclinata = True 
                        #per vedere la velocità del movimento in secondi
                        istante_inizio_discesa = datetime.now() 
                        f_discesa_veloce = False
                        f_discesa_lenta = False 
                        if f_direzione == "up":
                            f_direzione = "down"
                            counter+=1
                            #controllo velocità di salita
                            if (datetime.now() - istante_inizio_salita).total_seconds() < 1.5:
                                f_salita_veloce = True 
                            elif (datetime.now() - istante_inizio_salita).total_seconds() > 5:
                                f_salita_lenta = True
                        #se stai all'inizio  e su  
                        elif f_direzione == None: 
                            f_direzione="down"
                            counter = 0 
                        elif f_direzione == "down" and counter == 0:
                            #qua inizia il primo squat 
                            istante_inizio = datetime.now()
                    elif angle_dx < 60 and angle_sx < 60 and f_direzione == "down":  
                        f_direzione = "up" 
                        istante_inizio_salita = datetime.now() 
                        f_salita_veloce = False 
                        f_salita_lenta = False
                        #controllo velocità di discesa
                        if (datetime.now() - istante_inizio_discesa).total_seconds() < 0.5:
                            f_discesa_veloce = True
                        elif (datetime.now() - istante_inizio_discesa).total_seconds() > 5:
                            f_discesa_lenta = True 
                        if angle_schiena < 45:
                            f_schiena_troppo_inclinata = True
                        else:
                            f_schiena_troppo_inclinata = False 
                    elif f_direzione == None:
                        counter=0 

                    #controllo anomalie
                    if f_discesa_veloce or f_salita_veloce or f_discesa_lenta or f_salita_lenta or f_schiena_troppo_inclinata:
                        #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
                        if f_discesa_veloce or f_salita_veloce or f_discesa_lenta or f_salita_lenta:
                            cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 0, 255), -1) 
                        if f_discesa_veloce:
                            cv2.putText(image, "RALLENTA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                        elif f_salita_veloce:
                            cv2.putText(image, "RALLENTA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                        elif f_discesa_lenta:
                            cv2.putText(image, "VELOCIZZA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                        elif f_salita_lenta:
                            cv2.putText(image, "VELOCIZZA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                        if f_schiena_troppo_inclinata: 
                            cv2.rectangle(image_schiena, (0,int(a_image_schiena*0.125)+1), (int(l_image_schiena*0.75), int(a_image_schiena*0.25)), (0, 0, 255), -1)
                            cv2.putText(image_schiena, "SCHIENA TROPPO INCLINATA", (int(l_image_schiena*0.015), int(a_image_schiena*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))
                    else:
                        #vedi se counter è 0 (inizi a 100 gradi gambe ad esempio) che non ti deve mostrare OK, ma niente
                        if counter != 0:
                            #rettangolo verde se esecuzione ok image avanti
                            cv2.rectangle(image, (0,int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.25)), (0, 255, 0), -1)
                            cv2.putText(image, "OK", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

                            #rettangolo verde se esecuzione ok image schiena
                            cv2.rectangle(image_schiena, (0,int(a_image_schiena*0.125)+1), (int(l_image_schiena*0.5), int(a_image*0.25)), (0, 255, 0), -1)
                            cv2.putText(image_schiena, "OK", (int(l_image_schiena*0.015), int(a_image_schiena*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

                #mostra in alto a sinistra il contatore degli squat in un rettangolo verde 
                cv2.rectangle(image, (0,0), (int(l_image*0.55), int(a_image*0.125)), (0,255,0), -1)
                cv2.putText(image, "Squat :" + str(counter), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

                #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
                cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
                cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
                cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, cv2.LINE_AA)
                
                #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
                cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
                cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
                cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, cv2.LINE_AA)
                
                t_tot = round((datetime.now() - istante_inizio).total_seconds(), 1)       
            except:
                #eccezione quando il modello non vede alcun landmark
                pass

            #combina i due frame, uno affianco all'altro 
            img_composta = np.concatenate((image, cv2.resize(image_schiena,(l_image, a_image))), axis=1) 
            img_nuova = cv2.resize(img_composta, (larghezza_nuova, altezza_nuova))

            #mostro tempo trascorso in alto al centro 
            cv2.rectangle(img_nuova, (int(larghezza_nuova*0.8),int(altezza_nuova*0.01)) , (int(larghezza_nuova*0.98), int(altezza_nuova*0.1)), (255, 255, 255), -1)
            cv2.putText(img_nuova, str(t_tot), (int(larghezza_nuova*0.82), int(altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0))

            #crea popup con il video
            cv2.imshow("Assistente Fitness", img_nuova) 
            cv2.resizeWindow("Assistente Fitness", larghezza_nuova, altezza_nuova)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cap_schiena.release() 
        cv2.destroyAllWindows()