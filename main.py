import mediapipe
import cv2
import datetime

import excercises
import utility

import speech_recognition as sr

#GOOGLE API
def check_voice_command(recognizer, audio):
    #bisogna creare un dizionario di parole chiavi che interrompono
    l_grammar = ["stop", "ferma", "termina"]  
    #il programma se pronunciate
    try:
        # Riconosce il discorso
        text = recognizer.recognize_google(audio, language='it-IT')
        for parola in l_grammar:
            if parola in text.lower():
                #print("Esecuzione interrotta dall'input vocale.")
                # Se la parola chiave è rilevata, imposta una variabile globale per interrompere il ciclo
                global stop_vocal_command 
                stop_vocal_command = True
    except sr.UnknownValueError:
        pass  # Ignora l'errore se il discorso non è chiaro
    except sr.RequestError as e:
        #print(f"Errore nella richiesta al servizio di riconoscimento vocale: {e}")
        pass

if __name__ == "__main__":

    posture_detector = utility.PostureDetector()
    posture_detector1 = utility.PostureDetector()
    squat_counter = excercises.Squat(6)
    ui_manager_front = utility.UIManager(0)
    ui_manager_1 = utility.UIManager(1)

    wallsit = excercises.Static(10) 

    #GOOGLE API 
    #serve per capire quando terminare il programma
    stop_vocal_command = False 
    recognizer = sr.Recognizer() 
    microphone = sr.Microphone() 
    stop_listening = recognizer.listen_in_background(microphone, check_voice_command)
    
    tempo_sec = 0
    while ui_manager_front.cap.isOpened() and not stop_vocal_command :

        ret, frame = ui_manager_front.cap.read()
        ret_1, frame_1 = ui_manager_1.cap.read()
        try:
            #estraggo landmark, controllo visibilità e li mostro (webcam avanti)
            landmarks, results = posture_detector.detect_posture(frame)
            #print(landmarks)
        except:
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #print(ui_manager_front.larghezza_nuova, ui_manager_front.altezza_nuova)
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not ui_manager_front.display_frame(merged_frame):
                break
            continue 

        #questo non da errori neanche se non ci sono landmark
        frame, errore = posture_detector.check_landmarks(frame, ui_manager_front.l_image, ui_manager_front.a_image, landmarks, 0)
        if errore:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #print(ui_manager_front.larghezza_nuova, ui_manager_front.altezza_nuova)
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
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
            if tempo_sec > 0:
                #print(ui_manager_front.larghezza_nuova, ui_manager_front.altezza_nuova)
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not ui_manager_front.display_frame(merged_frame):
                break
            continue 

        #controllo visibilità landmark camera laterale 
        frame_1, errore_1 = posture_detector1.check_landmarks(frame_1, ui_manager_1.l_image, ui_manager_1.a_image, landmarks_1, 1)
        if errore_1:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #print(ui_manager_front.larghezza_nuova, ui_manager_front.altezza_nuova)
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not ui_manager_front.display_frame(merged_frame):
                break 
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame_1 = posture_detector1.draw_landmarks(frame_1, results_1.pose_landmarks)
        
        #calcolo angoli, li mostra e controllo corretta esecuzione (webcam avanti)
        asx, adx = posture_detector.calculate_angles(landmarks)
        frame = posture_detector.show_angles(frame, asx, posture_detector.knee_point_sx, ui_manager_front.l_image, ui_manager_front.a_image)
        frame = posture_detector.show_angles(frame, adx, posture_detector.knee_point_dx, ui_manager_front.l_image, ui_manager_front.a_image)
        #frame, tempo_sec = squat_counter.squat(frame, asx, adx, ui_manager_front.l_image, ui_manager_front.a_image, posture_detector.mp_pose, landmarks)
        
        #calcola angoli, li mostra e controllo agolazione schiena (camera laterale)
        absx, hip_sx = posture_detector1.calculate_angles_back(landmarks_1)
        frame_1 = posture_detector.show_angles(frame_1, absx, hip_sx, ui_manager_1.l_image, ui_manager_1.a_image)
        
        #frame_1 = squat_counter.back(frame_1, absx, landmarks_1, ui_manager_1.l_image, ui_manager_1.a_image, posture_detector.mp_pose, landmarks)
        frame, tempo_sec = wallsit.wallsit(frame, adx, asx, absx, ui_manager_front.a_image, ui_manager_front.l_image, posture_detector.mp_pose, landmarks)

        merged_frame = cv2.hconcat([frame, frame_1])
        #print(ui_manager_front.larghezza_nuova, ui_manager_front.altezza_nuova)
        cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
        #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
        cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
   
        if not ui_manager_front.display_frame(merged_frame):
            break

    #GOOGLE API         
    stop_listening(wait_for_stop = False)

    ui_manager_front.release_capture()
    ui_manager_1.release_capture() 

    ui_manager_final = utility.UIManager("no")  
    ui_manager_final.display_final_frame(squat_counter.count, tempo_sec)
    
    cv2.destroyAllWindows()