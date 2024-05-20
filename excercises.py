import cv2
from datetime import datetime
import datetime as dt

import utility

class Static:
    def __init__(self, sec):
        self.ending_instant = None
        self.sec = sec
        self.position = False
        self.real_ending_instant = None
        self.inizio_pausa = datetime.max
        self.sec_persi = 0
        #self.f_inizio_fuori = False
        self.istante_precedente_errore = datetime.min 
        self.istante_prec_ok = datetime.min 

    def wallsit(self, image, angle_dx, angle_sx, angle_back, a_image, l_image, mp_pose, landmarks):

        MAX_ANGLE = 105
        MIN_ANGLE = 85
        MAX_ANGLE_BACK = 110
        MIN_ANGLE_BACK = 90
        SOGLIA_SPALLE_CAVIGLIA = 0.8
        spalla_dx_x =  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x
        spalla_sx_x =  landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x
        caviglia_dx_x =  landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x
        caviglia_sx_x =  landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x

        if angle_dx < MAX_ANGLE and angle_dx > MIN_ANGLE and angle_sx < MAX_ANGLE and angle_sx > MIN_ANGLE and angle_back > MIN_ANGLE_BACK and angle_back < MAX_ANGLE_BACK  and ((min(spalla_dx_x, caviglia_dx_x) >= max(spalla_dx_x, caviglia_dx_x) * SOGLIA_SPALLE_CAVIGLIA) and (min(spalla_sx_x, caviglia_sx_x) >= max(spalla_sx_x, caviglia_sx_x) * SOGLIA_SPALLE_CAVIGLIA)) and not self.position:
            #quando entri per prima volta in posizione giusta
            self.istante_prec_ok = datetime.now() 
            #per vedere la velocità del movimento in secondi
            self.starting_instant = datetime.now() 
            #calcolo l'istante in cui deve finire l'esercizio
            self.ending_instant = self.starting_instant + dt.timedelta(seconds = self.sec)
            self.position = True
        elif angle_dx < MAX_ANGLE and angle_dx > MIN_ANGLE and angle_sx < MAX_ANGLE and angle_sx > MIN_ANGLE and angle_back > MIN_ANGLE_BACK and angle_back < MAX_ANGLE_BACK and ((min(spalla_dx_x, caviglia_dx_x) >= max(spalla_dx_x, caviglia_dx_x) * SOGLIA_SPALLE_CAVIGLIA) and (min(spalla_sx_x, caviglia_sx_x) >= max(spalla_sx_x, caviglia_sx_x) * SOGLIA_SPALLE_CAVIGLIA)) and self.position:
            self.istante_prec_ok = datetime.now() 
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.7), int(a_image*0.125)), (0,255,0), -1 , 20)
            cv2.putText(image, "Esercizio in esecuzione!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if self.istante_precedente_errore != datetime.min: 
                #vuodire che al frame prima stavo fuori, quindi conto l'intervallo 
                self.sec_persi += round((datetime.now() - self.istante_precedente_errore).total_seconds(), 1)
                self.istante_precedente_errore = datetime.min 
            if datetime.now() >= self.ending_instant: 
                #qua poi metti la voce che dice che hai finito
                #print("secondi persi in totale "+str(self.sec_persi))
                pass 

        if not(angle_dx < MAX_ANGLE and angle_dx > MIN_ANGLE and angle_sx < MAX_ANGLE and angle_sx > MIN_ANGLE and angle_back > MIN_ANGLE_BACK and angle_back < MAX_ANGLE_BACK and ((min(spalla_dx_x, caviglia_dx_x) >= max(spalla_dx_x, caviglia_dx_x) * SOGLIA_SPALLE_CAVIGLIA) and (min(spalla_sx_x, caviglia_sx_x) >= max(spalla_sx_x, caviglia_sx_x) * SOGLIA_SPALLE_CAVIGLIA))) and self.position:
            #calcolo intervallo tra ora e l'istante precedente, in cui stavo gia fuori
            if self.istante_prec_ok != datetime.min: 
                #se frame prima stavo ok
                self.sec_persi += round((datetime.now() - self.istante_prec_ok).total_seconds(), 1)
                self.istante_prec_ok = datetime.min 
            else:
                if self.istante_precedente_errore != datetime.min:
                    #se frame precedente stavo fuori 
                    self.sec_persi += round((datetime.now() - self.istante_precedente_errore).total_seconds(), 1)  
                self.istante_precedente_errore =  datetime.now() 
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(image, "Torna in posizione !", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
        """
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        """
        if self.position:
        #il secondo argomento calcola il tempo passato dall'inizio del 1 squat
            return image, round((datetime.now() - self.starting_instant).total_seconds(),1), datetime.now()
        return image, 0, datetime.now()

class Squat:
    def __init__(self, reps):
        self.starting_instant = datetime.now() #datetime.min 
        self.reps = reps
        self.current_direction = None
        self.count = 0 
        self.fast_up = False
        self.fast_d = False
        self.slow_up = False
        self.slow_d = False 
        self.current_position = None
        self.istante_inizio_discesa = datetime.now() 
        self.istante_inizio_salita = datetime.now()
        self.spalle_caviglia_problem = False 
        self.troppo_giu = False 

    def squat(self, image, angle_sx, angle_dx, l_image, a_image, mp_pose, landmarks, excercise = None):
        """
        controlla esecuzione squat con diverse modalità: apprendimento, endurance e explosive.
        """
        """ BISGONA AGGIUNGERE IL CONTROLLO TRA AMPIEZZA SPALLE E PIEDI, ok """ 
        TIME_SLOW = 2.5#5
        TIME_FAST = 1#1.5
        TIME_FASTD = 0.2#0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 100#60 #135
        MIN_ANGLE_DOWN = 60#45
        SOGLIA_SPALLE_CAVIGLIA = 0.8
        spalla_dx_x =  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x
        spalla_sx_x =  landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x
        caviglia_dx_x =  landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x
        caviglia_sx_x =  landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x

        if excercise == "E":
            TIME_SLOW = 6
            TIME_FAST = 4
            TIME_FASTD = 4
        
        elif excercise == "EX":
            TIME_SLOW = 2
            TIME_FAST = 0
            TIME_FASTD = 4
            MIN_ANGLE = 100 #85
            
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
                self.starting_instant = max(self.starting_instant, datetime.now()) 
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
        elif not(angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE) and not(angle_dx > MAX_ANGLE and angle_sx > MAX_ANGLE):
            self.current_position = "midle" 
        elif self.current_direction == None:
            self.count = 0 

        if angle_dx < MIN_ANGLE and angle_sx < MIN_ANGLE and (angle_dx < MIN_ANGLE_DOWN or angle_sx < MIN_ANGLE_DOWN) and self.current_direction == "up":
            #significa che sto troppo giu
            self.troppo_giu = True
            
        if (min(spalla_dx_x, caviglia_dx_x) < max(spalla_dx_x, caviglia_dx_x) * SOGLIA_SPALLE_CAVIGLIA) or (min(spalla_sx_x, caviglia_sx_x) < max(spalla_sx_x, caviglia_sx_x) * SOGLIA_SPALLE_CAVIGLIA) :
            #posizione sbagliata dei piedi e spalle
            self.spalle_caviglia_problem = True
        
        if self.fast_d or self.fast_up or self.slow_d or self.slow_up or self.spalle_caviglia_problem or self.troppo_giu:
            #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
            if self.fast_d:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Rallenta discesa!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            elif self.fast_up:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Rallenta salita!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
            elif self.slow_d:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Velocizza discesa!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
            elif self.slow_up:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Velocizza salita!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
            if self.spalle_caviglia_problem:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.375)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Spalle caviglia!", (int(l_image*0.015), int(a_image*0.442)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                self.spalle_caviglia_problem = False
            if self.troppo_giu:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.250)+5), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
                cv2.putText(image, "Troppo giu!", (int(l_image*0.015), int(a_image*0.317)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
                self.troppo_giu = False 
        else:
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.5), int(a_image*0.125)), (0,255,0), -1 , 20)
            #rettangolo verde se esecuzione è ok
            if self.current_position == "up" and self.count == 0:
                #quando stai in posizione iniziale giusta
                cv2.putText(image, "Puoi iniziare ora!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)  
            elif self.current_direction == "up":
                cv2.putText(image, "Ok, ora su!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)  
            elif self.current_direction == "down":
                cv2.putText(image, "Ok, ora giu!", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)    

        #mostra in alto a sinistra il contatore degli squat in un 
        #rettangolo verde 
        utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.005)), (int(l_image*0.55), int(a_image*0.125)), (0,255,0), -1 , 20)
        cv2.putText(image, "Squat: " + str(self.count), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, 16)
        """
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        """
        #il secondo argomento calcola il tempo passato dall'inizio del 1 squat
        return image, round((datetime.now() - self.starting_instant).total_seconds(),1) 
    

    def back(self, image, angle_back, landmarks, l_image, a_image, mp_pose):
        """ BISOGNA VEDERE BENE GLI ANGOLI DURANTE LA DISCESA, ok """
        ANGLE_BACK_UP = 130
        ANGLE_BACK_DOWN = 30
        
        if ((self.current_position == "up" and  angle_back < ANGLE_BACK_UP) or (self.current_position == "down" and  angle_back < ANGLE_BACK_DOWN)) and (self.current_position != "midle"):
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+5), (int(l_image*0.75), int(a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(image, "SCHIENA TROPPO INCLINATA", (int(l_image*0.015), int(a_image*0.190)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
        """
        #Mostra le visibility di spalla, anca e ginocchio sx nel frame laterale
        cv2.putText(image, "spalla sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        """
        return image
