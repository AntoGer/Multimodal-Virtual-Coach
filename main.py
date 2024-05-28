import cv2
from datetime import datetime

import excercises
import utility

import speech_recognition as sr

from tkinter import *
import customtkinter

import datetime as dt
import winsound


def ex_squat():

    posture_detector = utility.PostureDetector()
    posture_detector1 = utility.PostureDetector() 
    
    ui_manager_front = utility.UIManager(0)
    ui_manager_1 = utility.UIManager(1)


    #qua voglio mettere una voce che ti dice quante ripetizioni vuoi fare, altrimenti dici libero
    #e poi metti controllo in Squat per vedere se arrivi a lla soglia di ripetizioni prefissata 
    #Google speech recognition prende numero  come intero e non come testo (se dico venti => 20)
    
    info_squat = utility.Get_info_squat() 
    info_squat.run() 
    if info_squat.tipo_esercizio == "esercizio libero":
        squat_counter = excercises.Squat(info_squat.tipo_esercizio)
    else: 
        #significa che vuoi fare una serie
        squat_counter = excercises.Squat(info_squat.tipo_esercizio,info_squat.num_serie, info_squat.num_ripetizioni, info_squat.sec_recupero)

    scelta = info_squat.tipo_esercizio
    tempo_sec = 0  
    vcom_stop = utility.Speech_interaction(["stop", "ferma", "termina", "fine", "finisci", "esci"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)
    
    utility.pronuncia("In ogni momento puoi dire stop, ferma, termina, fine, finisci, esci oppure premere q per terminare la sessione")

    while ui_manager_front.cap.isOpened() and not vcom_stop.vocal_command:
        if scelta == "serie" and squat_counter.count_serie == squat_counter.num_serie:
            #se faccio le serie e completo quelle che avevo prefissato come obiettivo allora esci dal ciclo
            break 
        ret, frame = ui_manager_front.cap.read()
        ret_1, frame_1 = ui_manager_1.cap.read()
        #lo faccio per far in modo che il messaggio Tieniti pronto che appare durante la pausa tra una serie e lp'altra rimane anche se esci dall'inquadratura
        try:
            if squat_counter.tipo_esercizio == "serie" and datetime.now() >= squat_counter.istante_inizio_pausa and datetime.now() <= squat_counter.istante_fine_pausa: 
            #significa che sto in periodo di pausa tra una serie e l'altra e non devo fare esercizio
                if datetime.now() > squat_counter.istante_fine_pausa - dt.timedelta(seconds = 3):
                    utility.draw_rectangle(frame, (int(ui_manager_front.l_image*0.005), int(ui_manager_front.a_image*0.125)+5), (int(ui_manager_front.l_image*0.42), int(ui_manager_front.a_image*0.125)), (0,255,255), -1 , 20)
                    cv2.putText(frame, "Tieniti pronto!", (int(ui_manager_front.l_image*0.015), int(ui_manager_front.a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    winsound.Beep(1500, 500) 
                else:
                    utility.draw_rectangle(frame, (int(ui_manager_front.l_image*0.005), int(ui_manager_front.a_image*0.125)+5), (int(ui_manager_front.l_image*0.18), int(ui_manager_front.a_image*0.125)), (0,255,0), -1 , 20)
                    cv2.putText(frame, "Pausa!", (int(ui_manager_front.l_image*0.015), int(ui_manager_front.a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)  
        except:
            pass

        try:
            #estraggo landmark, controllo visibilità e li mostro (webcam avanti)
            landmarks, results = posture_detector.detect_posture(frame)
            #print(landmarks)
        except:
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            utility.draw_rectangle(merged_frame, (int(ui_manager_front.l_image*0.005), int(ui_manager_front.a_image*0.005)), (int(ui_manager_front.l_image*0.33), int(ui_manager_front.a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(merged_frame, "Non ti vedo!", (int(ui_manager_front.l_image*0.015), int(ui_manager_front.a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if tempo_sec > 0:
                #timer bianco
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #utility.draw_rectangle(merged_frame, (int(ui_manager_front.l_image*0.45),int(ui_manager_front.a_image*0.005)), (int(ui_manager_front.l_image*0.55), int(ui_manager_front.a_image*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not (ui_manager_front.display_frame(merged_frame)):
                break
            continue 
        
        #estraggo landmark e li mostro (camera laterale)
        try:
            landmarks_1, results_1 = posture_detector1.detect_posture(frame_1)
        except :
            #se non vede nessuno lancia l'eccezione
            utility.draw_rectangle(frame_1, (int(ui_manager_1.l_image*0.005), int(ui_manager_1.a_image*0.005)), (int(ui_manager_1.l_image*0.33), int(ui_manager_1.a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(frame_1, "Non ti vedo!", (int(ui_manager_1.l_image*0.015), int(ui_manager_1.a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #timer bianco
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not (ui_manager_front.display_frame(merged_frame)):
                break
            continue

        #questo non da errori neanche se non ci sono landmark
        frame, errore = posture_detector.check_landmarks(frame, ui_manager_front.l_image, ui_manager_front.a_image, landmarks, 0)
        if errore:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:                
                #timer bianco
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not (ui_manager_front.display_frame(merged_frame)):
                break  
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame = posture_detector.draw_landmarks(frame, results.pose_landmarks)

        #controllo visibilità landmark camera laterale 
        frame_1, errore_1 = posture_detector1.check_landmarks(frame_1, ui_manager_1.l_image, ui_manager_1.a_image, landmarks_1, 1)
        if errore_1:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #timer bianco
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not (ui_manager_front.display_frame(merged_frame)):
                break 
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame_1 = posture_detector1.draw_landmarks(frame_1, results_1.pose_landmarks)
        
        #calcolo angoli, li mostra e controllo corretta esecuzione (webcam avanti)
        asx, adx = posture_detector.calculate_angles(landmarks)
        frame = posture_detector.show_angles(frame, asx, posture_detector.knee_point_sx, ui_manager_front.l_image, ui_manager_front.a_image)
        frame = posture_detector.show_angles(frame, adx, posture_detector.knee_point_dx, ui_manager_front.l_image, ui_manager_front.a_image)
        
        #calcola angoli, li mostra e controllo agolazione schiena (camera laterale)
        absx, hip_sx = posture_detector1.calculate_angles_back(landmarks_1)
        frame_1 = posture_detector1.show_angles(frame_1, absx, hip_sx, ui_manager_1.l_image, ui_manager_1.a_image)
        
        frame, tempo_sec = squat_counter.squat(frame, asx, adx, ui_manager_front.l_image, ui_manager_front.a_image, posture_detector.mp_pose, landmarks)
        frame_1 = squat_counter.back(frame_1, absx, landmarks_1, ui_manager_1.l_image, ui_manager_1.a_image, posture_detector.mp_pose)

        merged_frame = cv2.hconcat([frame, frame_1])
        #timer viola
        cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
        #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
        cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
   
        if not (ui_manager_front.display_frame(merged_frame)):
            break

    #ui_manager_final.display_final_frame_squat(squat_counter.count_squat, tempo_sec)
    #GOOGLE API         
    stop_listening(wait_for_stop = False) 
    ui_manager_front.display_final_frame_squat(squat_counter.count_squat, tempo_sec) 
    ui_manager_front.release_capture()
    ui_manager_1.release_capture()
    cv2.destroyAllWindows() 

def ex_wallsit():

    posture_detector = utility.PostureDetector()
    posture_detector1 = utility.PostureDetector() 
    
    ui_manager_front = utility.UIManager(0)
    ui_manager_1 = utility.UIManager(1)

    tempo_sec = 0

    info_wallsit = utility.Get_info_wallsit() 
    info_wallsit.run() 
    #durata prevista dell'esercizio
    tempo_wallsit = info_wallsit.num_sec
    wallsit = excercises.Static()
    
    vcom_stop = utility.Speech_interaction(["stop", "ferma", "termina", "fine", "finisci", "esci"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)
    istante_ultimo_wallsit = None 
    
    utility.pronuncia("In ogni momento puoi dire stop, ferma, termina, fine, finisci, esci oppure premere q per terminare la sessione")

    while ui_manager_front.cap.isOpened() and not vcom_stop.vocal_command :

        ret, frame = ui_manager_front.cap.read()
        ret_1, frame_1 = ui_manager_1.cap.read()
        try:
            #estraggo landmark, controllo visibilità e li mostro (webcam avanti)
            landmarks, results = posture_detector.detect_posture(frame) 
        except:
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            utility.draw_rectangle(merged_frame, (int(ui_manager_front.l_image*0.005), int(ui_manager_front.a_image*0.005)), (int(ui_manager_front.l_image*0.33), int(ui_manager_front.a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(merged_frame, "Non ti vedo!", (int(ui_manager_front.l_image*0.015), int(ui_manager_front.a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if tempo_sec > 0:
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_wallsit != None and tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
            if not (ui_manager_front.display_frame(merged_frame)) or (tempo_wallsit != None and tempo_sec > tempo_wallsit):
                break
            continue 
        
        #estraggo landmark e li mostro (camera laterale)
        try:
            landmarks_1, results_1 = posture_detector1.detect_posture(frame_1)
        except :
            #se non vede nessuno lancia l'eccezione
            utility.draw_rectangle(frame_1, (int(ui_manager_1.l_image*0.005), int(ui_manager_1.a_image*0.005)), (int(ui_manager_1.l_image*0.33), int(ui_manager_1.a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(frame_1, "Non ti vedo!", (int(ui_manager_1.l_image*0.015), int(ui_manager_1.a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_wallsit != None and tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
            if not (ui_manager_front.display_frame(merged_frame)) or (tempo_wallsit != None and tempo_sec > tempo_wallsit):
                break
            continue

        #questo non da errori neanche se non ci sono landmark
        frame, errore = posture_detector.check_landmarks(frame, ui_manager_front.l_image, ui_manager_front.a_image, landmarks, 0)
        if errore:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_wallsit != None and tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
            if not (ui_manager_front.display_frame(merged_frame)) or (tempo_wallsit != None and tempo_sec > tempo_wallsit):
                break  
            continue
        #qui non può dare errore perchè i landmark ce li hai per forza 
        frame = posture_detector.draw_landmarks(frame, results.pose_landmarks)

        #controllo visibilità landmark camera laterale 
        frame_1, errore_1 = posture_detector1.check_landmarks(frame_1, ui_manager_1.l_image, ui_manager_1.a_image, landmarks_1, 1)
        if errore_1:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_wallsit != None and tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
            if not (ui_manager_front.display_frame(merged_frame)) or (tempo_wallsit != None and tempo_sec > tempo_wallsit):
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
        frame_1 = posture_detector1.show_angles(frame_1, absx, hip_sx, ui_manager_1.l_image, ui_manager_1.a_image)
         
        frame, tempo_sec, istante_ultimo_wallsit = wallsit.wallsit(frame, adx, asx, absx, ui_manager_front.a_image, ui_manager_front.l_image, posture_detector.mp_pose, landmarks)
        #print("secondi persi "+str(wallsit.sec_persi))
        merged_frame = cv2.hconcat([frame, frame_1])
        #timer viola
        cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
        #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
        cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
   
        if not (ui_manager_front.display_frame(merged_frame)) or (tempo_wallsit != None and tempo_sec > tempo_wallsit):
            break
    #ui_manager_final.display_final_frame_wallsit(tempo_wallsit, sec_persi)
    #GOOGLE API         
    stop_listening(wait_for_stop = False) 
    if istante_ultimo_wallsit != None:
        ui_manager_front.display_final_frame_wallsit(tempo_wallsit, wallsit.sec_persi, wallsit.position, tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1))
    else:
        ui_manager_front.display_final_frame_wallsit(tempo_wallsit, wallsit.sec_persi, wallsit.position, tempo_sec)
    ui_manager_front.release_capture()
    ui_manager_1.release_capture()
    cv2.destroyAllWindows() 
    
def ex_workout():
    #label.config(text="workout")
    ex_squat()
    ex_wallsit()

# Funzione per uscire dal programma
def esci():
    root.destroy()

if __name__ == "__main__": 

    #GOOGLE API 
    #serve per capire quando terminare il programma
    #vcom_stop = utility.Speech_interaction(["stop", "ferma", "termina", "fine", "finisci", "esci"])
    #stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)

    #Setting up theme of your app, or light
    customtkinter.set_appearance_mode("dark")

    #cambia colore bottoni
    customtkinter.set_default_color_theme("green")

    # Creazione della finestra principale
    root = customtkinter.CTk()
    root.title("Menu")
    root.geometry(f"{400}x{400}")

    # Etichetta per visualizzare il risultato dell'azione selezionata
    #label = Label(root, text="")
    #label.pack()

    logo_label = customtkinter.CTkLabel(master=root, text="Esercizi", font=customtkinter.CTkFont(size=20, weight="bold"))
    logo_label.place(relx=0.5, rely=0.1, anchor=CENTER)
    #logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

    # Creazione dei bottoni per le azioni
    button1 = customtkinter.CTkButton(master=root, text="Squat", command=ex_squat)
    button1.place(relx=0.5, rely=0.3, anchor=CENTER)

    # Creazione dei bottoni per le azioni
    button2 = customtkinter.CTkButton(master=root, text="Wallsit", command=ex_wallsit)
    button2.place(relx=0.5, rely=0.4, anchor=CENTER)

    # Creazione dei bottoni per le azioni
    button3 = customtkinter.CTkButton(master=root, text="Workout", command=ex_workout)
    button3.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Bottone per uscire dal programma
    # Creazione dei bottoni per le azioni
    button_exit = customtkinter.CTkButton(master=root, text="Esci", command=esci)
    button_exit.place(relx=0.5, rely=0.7, anchor=CENTER)

    #ui_manager_final = utility.UIManager("no") 
    root.mainloop()

    #GOOGLE API         
    #stop_listening(wait_for_stop = False) 

    cv2.destroyAllWindows()