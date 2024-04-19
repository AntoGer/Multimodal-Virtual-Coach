import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

import cv2

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

import time

model_path = 'pose_landmarker_lite.task'

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), result)
    cv2.imshow("img", annotated_image)
    #print('pose landmarker result: {}'.format(result))


model_file = open('pose_landmarker_lite.task', "rb")
model_data = model_file.read()
model_file.close()
    
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_buffer=model_data),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
    )

cap = cv2.VideoCapture(0) 

with PoseLandmarker.create_from_options(options) as landmarker:
  # The landmarker is initialized. Use it here.
  # ...

    while True:
        ret, frame = cap.read()
        
        #cv2 cattura frame in BGR e non RGB
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        timestamp_ms = int(time.time() * 1000)

        landmarker.detect_async(mp_image, timestamp_ms)  

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()     
cv2.destroyAllWindows()
