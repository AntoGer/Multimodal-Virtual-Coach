import cv2
from datetime import datetime
import time

import excercises
import utility

import speech_recognition as sr

from tkinter import *
import customtkinter

import pyttsx3
import re
def ex_squat():

    posture_detector = utility.PostureDetector()
    posture_detector1 = utility.PostureDetector() 
    
    ui_manager_front = utility.UIManager(0)
    ui_manager_1 = utility.UIManager(1)


    #qua voglio mettere una voce che ti dice quante ripetizioni vuoi fare, altrimenti dici libero
    #e poi metti controllo in Squat per vedere se arrivi a lla soglia di ripetizioni prefissata 
    #Google speech recognition prende numero  come intero e non come testo (se dico venti => 20)
    
    engine = pyttsx3.init() 
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 200)
    engine.setProperty('voice', voices[0].id )
    #for voce in voices:    
    #    print("ECCO ",voce, " FINE") 
    engine.say("Quante ripetizioni vuoi fare da 1 a 20? Altrimenti di :esercizio libero, per farne quante ne vuoi")
    engine.runAndWait() 
    #per le risposte, avvolte lo speech recognition scrive la cifra e altre volte la parola
    dict_num = {"uno":1, "due":2, "tre":3, "quattro":4,"cinque":5,"sei":6,"sette":7,"otto":8,"nove":9,"dieci":10,"undici":1,"dodici":12,"tredici":13,"quattordici":14,"quindici":15,"sedici":16,"diciassette":17, "diciotto":18,"diciannove":19,"venti":20}
    # obtain audio from the microphone
    r = sr.Recognizer()
    scelta = None
    f = False
    with sr.Microphone() as source:
        print("Rispondi ora") 
        while True:
            audio = r.listen(source)
            try:
                scelta =  r.recognize_google(audio, language="it-IT")
                print("primo input "+scelta ) 
                if "esercizio libero" in scelta.lower():
                    scelta = 1000
                    break
                numero = re.search(r'\d+', scelta)
                if numero:
                    #significa che c'è un numero gia come intero stringa
                    scelta = int(numero.group())
                    print("Google Speech Recognition thinks you said " +str(scelta))
                    break 
                for num in dict_num:
                    #se lo scrive a parole
                    if num in scelta.split():
                        scelta = dict_num[num] 
                        f = True
                        print("Google Speech Recognition thinks you said " +str(scelta))
                        break  
                if f:
                    break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print("Ok, facciamo "+ str(scelta)+ " squat")
    num_squat = scelta 
    squat_counter = excercises.Squat(num_squat)
    tempo_sec = 0  
    vcom_stop = utility.speech_interaction(["stop", "ferma", "termina", "fine", "finisci"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)
    
    
    #while ui_manager_front.cap.isOpened() and not vocal_command and squat_counter.count < num_squat:
    while ui_manager_front.cap.isOpened() and not vcom_stop.vocal_command and squat_counter.count < num_squat:
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
        
        #estraggo landmark e li mostro (camera laterale)
        try:
            landmarks_1, results_1 = posture_detector1.detect_posture(frame_1)
        except :
            #se non vede nessuno lancia l'eccezione
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                #timer bianco
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(round((datetime.now() - squat_counter.starting_instant).total_seconds(),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if not (ui_manager_front.display_frame(merged_frame)):
                break
            continue 

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

    #ui_manager_final.display_final_frame_squat(squat_counter.count, tempo_sec)
    #GOOGLE API         
    stop_listening(wait_for_stop = False) 
    ui_manager_front.display_final_frame_squat(squat_counter.count, tempo_sec) 
    ui_manager_front.release_capture()
    ui_manager_1.release_capture()
    cv2.destroyAllWindows() 

def ex_wallsit():

    posture_detector = utility.PostureDetector()
    posture_detector1 = utility.PostureDetector() 
    
    ui_manager_front = utility.UIManager(0)
    ui_manager_1 = utility.UIManager(1)

    tempo_sec = 0

    engine = pyttsx3.init() 
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 200)
    engine.setProperty('voice', voices[0].id )
    #for voce in voices:    
    #    print("ECCO ",voce, " FINE") 
    engine.say("Quante secondi da 1 a 20? Altrimenti di :esercizio libero, per farne quante ne vuoi")
    engine.runAndWait() 
    #per le risposte, avvolte lo speech recognition scrive la cifra e altre volte la parola
    dict_num = {"uno":1, "due":2, "tre":3, "quattro":4,"cinque":5,"sei":6,"sette":7,"otto":8,"nove":9,"dieci":10,"undici":11,"dodici":12,"tredici":13,"quattordici":14,"quindici":15,"sedici":16,"diciassette":17, "diciotto":18,"diciannove":19,"venti":20}
    # obtain audio from the microphone
    r = sr.Recognizer()
    scelta = None
    f = False
    with sr.Microphone() as source:
        print("Rispondi ora") 
        while True:
            audio = r.listen(source)
            try:
                scelta =  r.recognize_google(audio, language="it-IT")
                print("primo input "+scelta ) 
                if "esercizio libero" in scelta.lower():
                    scelta = 1000
                    break
                numero = re.search(r'\d+', scelta)
                if numero:
                    #significa che c'è un numero gia come intero stringa
                    scelta = int(numero.group())
                    print("Google Speech Recognition thinks you said " +str(scelta))
                    break 
                for num in dict_num:
                    #se lo scrive a parole
                    if num in scelta.split():
                        scelta = dict_num[num] 
                        f = True
                        print("Google Speech Recognition thinks you said " +str(scelta))
                        break  
                if f:
                    break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print("Ok, facciamo "+ str(scelta)+ " secondi") 
    #durata prevista dell'esercizio
    tempo_wallsit = scelta #10
    wallsit = excercises.Static(tempo_wallsit)
    
    vcom_stop = utility.speech_interaction(["stop", "ferma", "termina", "fine", "finisci"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)
    istante_ultimo_wallsit = None 

    while ui_manager_front.cap.isOpened() and not vcom_stop.vocal_command :

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
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
                #timer viola
                """cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                """
            if not (ui_manager_front.display_frame(merged_frame)) or tempo_sec > tempo_wallsit:
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
                    if tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
                #timer viola
                """cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                """
            if not (ui_manager_front.display_frame(merged_frame)) or tempo_sec > tempo_wallsit:
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
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
                """#timer viola
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                """
            if not (ui_manager_front.display_frame(merged_frame)) or tempo_sec > tempo_wallsit:
                break
            continue 

        #controllo visibilità landmark camera laterale 
        frame_1, errore_1 = posture_detector1.check_landmarks(frame_1, ui_manager_1.l_image, ui_manager_1.a_image, landmarks_1, 1)
        if errore_1:
            merged_frame = cv2.hconcat([frame, frame_1])
            if tempo_sec > 0:
                if istante_ultimo_wallsit != None:
                    cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                    #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                    cv2.putText(merged_frame, str(round(tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1),1)), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                    if tempo_sec + round((datetime.now()-istante_ultimo_wallsit).total_seconds(),1) > tempo_wallsit:
                        break
                """#timer viola
                cv2.rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 0, 255), -1)
                #draw_rectangle(merged_frame, (int(ui_manager_front.larghezza_nuova*0.45),int(ui_manager_front.altezza_nuova*0.005)), (int(ui_manager_front.larghezza_nuova*0.55), int(ui_manager_front.altezza_nuova*0.06)), (255, 255, 255), -1 , 20)
                cv2.putText(merged_frame, str(tempo_sec), (int(ui_manager_front.larghezza_nuova*0.475), int(ui_manager_front.altezza_nuova*0.05)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                """
            if not (ui_manager_front.display_frame(merged_frame)) or tempo_sec > tempo_wallsit:
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
   
        if not (ui_manager_front.display_frame(merged_frame)) or tempo_sec > tempo_wallsit:
            break
    #ui_manager_final.display_final_frame_wallsit(tempo_wallsit, sec_persi)
    #GOOGLE API         
    stop_listening(wait_for_stop = False) 
    ui_manager_front.display_final_frame_wallsit(tempo_wallsit, wallsit.sec_persi, wallsit.position)
    
    ui_manager_front.release_capture()
    ui_manager_1.release_capture()
    cv2.destroyAllWindows() 
    
def ex_workout():
    #label.config(text="workout")
    pass

# Funzione per uscire dal programma
def esci():
    root.destroy()

if __name__ == "__main__": 

    #GOOGLE API 
    #serve per capire quando terminare il programma
    vcom_stop = utility.speech_interaction(["stop", "ferma", "termina", "fine", "finisci"])
    stop_listening = vcom_stop.recognizer.listen_in_background(vcom_stop.microphone, vcom_stop.check_voice_command)

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
    stop_listening(wait_for_stop = False) 

    cv2.destroyAllWindows()