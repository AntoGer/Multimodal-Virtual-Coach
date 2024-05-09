import cv2
from datetime import datetime
import datetime as dt

import utility

class Static:
    def __init__(self, sec):
        #self.starting_instant = None
        #self.seconds = 0
        self.ending_instant = None
        self.sec = sec
        self.position = False

    def wallsit(self, image, angle_dx, angle_sx, angle_back, a_image, l_image, mp_pose, landmarks):

        MAX_ANGLE = 100
        MIN_ANGLE = 80

        #contatore degli squat e controllo sulle velocità di esecuzione
        #160 è troppo  

        if angle_dx < MAX_ANGLE and angle_sx > MIN_ANGLE and angle_back > 85 and angle_back < 95  and not self.position:
            #per vedere la velocità del movimento in secondi
            self.starting_instant = datetime.now() 
            self.ending_instant = self.starting_instant + dt.timedelta(seconds = self.sec)
            self.position = True
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.125)), (0,255,0), -1 , 20)
            cv2.putText(image, "Esercizio iniziato!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
        elif angle_dx < MAX_ANGLE and angle_sx > MIN_ANGLE and angle_back > 85 and angle_back < 95  and  self.position:
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.125)), (0,255,0), -1 , 20)
            cv2.putText(image, "Esercizio in esecuzione!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            if datetime.now() >= self.ending_instant:#self.starting_instant + self.seconds:
                utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.125)), (0,255,0), -1 , 20)
                cv2.putText(image, "Esercizio finito!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16) 


        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        
        if self.position:
        #il secondo argomento calcola il tempo passato dall'inizio del 1 squat
            return image, round((datetime.now() - self.starting_instant).total_seconds(),1)  
        return image, 0  

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

    def squat(self, image, angle_sx, angle_dx, l_image, a_image, mp_pose, landmarks, excercise=None):
        """
        controlla esecuzione squat con diverse modalità: apprendimento, endurance e explosive.
        """
        TIME_SLOW = 5
        TIME_FAST = 1.5
        TIME_FASTD = 0.5
        MAX_ANGLE = 140
        MIN_ANGLE = 60 #135

        if excercise == "E":
            TIME_SLOW = 6
            TIME_FAST = 4
            TIME_FASTD = 4
        
        elif excercise == "EX":
            TIME_SLOW = 2
            TIME_FAST = 0
            TIME_FASTD = 4
            MIN_ANGLE = 85

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
        elif self.current_direction == None:
            self.count = 0 

        if self.fast_d or self.fast_up or self.slow_d or self.slow_up:
            #rettangolo rosso se sceso o salgo troppo veloce o se scendo o salgo troppo lentamente
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.125)), (0,0,255), -1 , 20)
            if self.fast_d:
                cv2.putText(image, "RALLENTA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)
            elif self.fast_up:
                cv2.putText(image, "RALLENTA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
            elif self.slow_d:
                cv2.putText(image, "VELOCIZZA DISCESA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
            else:
                cv2.putText(image, "VELOCIZZA SALITA!", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2, 16)
        else:
            #rettangolo verde se esecuzione
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.5), int(a_image*0.125)), (0,255,0), -1 , 20)
            cv2.putText(image, "OK", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)    

        #mostra in alto a sinistra il contatore degli squat in un 
        #rettangolo verde 
        utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.005)), (int(l_image*0.55), int(a_image*0.125)), (0,255,0), -1 , 20)
        cv2.putText(image, "Squat :" + str(self.count), (int(l_image*0.015), int(a_image*0.065)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, 16)
        

        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility*100)),(int(l_image*0.055),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "ginocchio dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility*100)),(int(l_image*0.055),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        cv2.putText(image, "caviglia dx "+ str(int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility*100)),(int(l_image*0.055),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(255,144,30), 2, 16)
        
        #Mostra le visibility di anca, ginocchio e caviglia dx nel frame
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "caviglia sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        
        #il secondo argomento calcola il tempo passato dall'inizio del 1 squat
        return image, round((datetime.now() - self.starting_instant).total_seconds(),1) 
    

    def back(self, image, angle_back, landmarks, l_image, a_image, mp_pose):
        ANGLE_BACK_UP = 130
        ANGLE_BACK_DOWN = 30

        if (self.current_position == "up" and  angle_back < ANGLE_BACK_UP) or (self.current_position == "down" and  angle_back < ANGLE_BACK_DOWN):
            utility.draw_rectangle(image, (int(l_image*0.005), int(a_image*0.125)+1), (int(l_image*0.75), int(a_image*0.125)), (0,0,255), -1 , 20)
            cv2.putText(image, "SCHIENA TROPPO INCLINATA", (int(l_image*0.015), int(a_image*0.187)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, 16)

        #Mostra le visibility di spalla, anca e ginocchio sx nel frame laterale
        cv2.putText(image, "spalla sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility*100)),(int(l_image*0.55),int(a_image*0.855)),cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "anca sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility*100)),(int(l_image*0.55),int(a_image*0.917)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
        cv2.putText(image, "ginocchio sx "+ str(int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility*100)),(int(l_image*0.55),int(a_image*0.98)), cv2.FONT_HERSHEY_SIMPLEX, 1 ,(0,140,255), 2, 16)
    
        return image
