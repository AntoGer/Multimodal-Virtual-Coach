# Multimodal-interaction
Multimodal-interaction exam project

This project aimed to develop a virtual personal trainer that thanks to two cameras can track different kinds of exercise and support the user through guided workouts and audio and video hints and corrections.

In this project, we focused on multimodality, and so there different technology we imported from Google as: MediaPipe for the pose estimation, google speech_recognition.

In particular, we use 2 different cameras to capture video from different angles to better estimate the position of the user in each frame in real-time, to achive a high precision in angols calculus. To estimate the landmarkesr and obtain the information abpout the angels we use two different mediapipe pose estimation models, one for each camera, the frontal one is resposible to check that thers the right distance between legs and that the backbone is alignated. the side camera ensure if the body is to exposed in the front or on ther back and calculates the angle of the hip and knee.

![Alt text](./images/selezione_esercizio.png)

cit.
https://www.breakfreephysiotherapy.ca/blog/low-back-pain-from-squats

Executing the main.py script, you will launch the app and display the menu.

![Alt text](./images/selezione_esercizio.png)

Here you can select one particular exercise or start a workout:

Squat: in the quat exercise you will be asked, thanks to the voice synthesiser, to tell some information about the exercise, such as how many repetitions, sets and the recovery time all through speech interaction.
This operation has to be improved because it depends a lot on your internet connection (Google Speech recognition just records the audio and sends it to a server to analyze it) but once it is done the exercise will start and you should see landmarks appear on your body.

![Alt text](./images/squat_inizio_ok.png)
