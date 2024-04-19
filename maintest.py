import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import cv2

model_path = 'pose_landmarker_lite.task'

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print('pose landmarker result: {}'.format(result))

model_file = open("/content/drive/My Drive/Colab Notebooks/pose_landmarker_heavy.task", "rb")
model_data = model_file.read()
model_file.close()
    
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_buffer=model_data),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

cap = cv2.VideoCapture(0) 

with PoseLandmarker.create_from_options(options) as landmarker:
  # The landmarker is initialized. Use it here.
  # ...
    
    while True:
        ret, frame = cap.read()
        
        #cv2 cattura frame in BGR e non RGB
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
        # Use OpenCV’s VideoCapture to start capturing from the webcam.

        # Create a loop to read the latest frame from the camera using VideoCapture#read()

        # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        out = timestamp_ms = (cv2.getTickCount() / cv2.getTickFrequency()) * 1000

        # Send live image data to perform pose landmarking.
        # The results are accessible via the `result_callback` provided in
        # the `PoseLandmarkerOptions` object.
        # The pose landmarker must be created with the live stream mode.
        landmarker.detect_async(mp_image, timestamp_ms)
        cv2.imshow("img", cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()     
cv2.destroyAllWindows()
