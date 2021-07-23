import mediapipe as mp
import cv2
import math

# Configuration options
MOVEMENT_SMOOTHNESS = 25
ROTATION_SMOOTHNESS = 15
ROTATION_THRESHOLD = 5

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(1)
success, original_image = cap.read()
WINDOW_WIDTH = original_image.shape[1]
WINDOW_HEIGHT = original_image.shape[0]
# Recommended factor
MARGINFACTOR = 0.3
MINIMUM_FACE_HEIGHT = 150
MINIMUM_HEAD_WIDTH = 80
coords_storage = [[0, 0, 0, 0, 0, [0, 0]]] * MOVEMENT_SMOOTHNESS


def getKeypoint(detection, keypoint):
    return round(mp_face_detection.get_key_point(detection, keypoint).x * WINDOW_WIDTH), round(
        mp_face_detection.get_key_point(detection, keypoint).y * WINDOW_HEIGHT)


def computeCropping(detection):
    nose_x, nose_y = getKeypoint(
        detection, mp_face_detection.FaceKeyPoint.NOSE_TIP)
    left_ear_x, left_ear_y = getKeypoint(
        detection, mp_face_detection.FaceKeyPoint.LEFT_EAR_TRAGION)
    right_ear_x, right_ear_y = getKeypoint(
        detection, mp_face_detection.FaceKeyPoint.RIGHT_EAR_TRAGION)
    mouth_x, mouth_y = getKeypoint(
        detection, mp_face_detection.FaceKeyPoint.MOUTH_CENTER)
    left_eye_x, left_eye_y = getKeypoint(
        detection, mp_face_detection.FaceKeyPoint.LEFT_EYE)
    nose_lenght = nose_y - left_eye_y
    head_width = left_ear_x - right_ear_x
    if head_width < MINIMUM_HEAD_WIDTH:
        head_width = MINIMUM_HEAD_WIDTH
    if nose_lenght < MINIMUM_FACE_HEIGHT:
        nose_lenght = MINIMUM_FACE_HEIGHT
    computed_coords = [
        round(right_ear_x - head_width / 2 * (1 + MARGINFACTOR)),
        round(left_eye_y - nose_lenght / 2 * (1 + MARGINFACTOR)),
        round(left_ear_x + head_width / 2 * (1 + MARGINFACTOR)),
        round(mouth_y + nose_lenght / 2 * (1 + MARGINFACTOR)),
        computeAngle(left_ear_x, right_ear_x, left_ear_y, right_ear_y, ),
        (nose_x, nose_y)
    ]
    return computed_coords


def validateCropping(original_coords):
    #                         rotationswinkel,    rotationspunkt benötigen keine Validierung
    new_coords = [0, 0, 0, 0, original_coords[4], original_coords[5]]
    # Wenn das Bild rechts anstößt, überprüfe, ob er auch noch nach unten oder oben anstößt
    if original_coords[2] >= WINDOW_WIDTH:
        new_coords[2] = WINDOW_WIDTH - 1
        if original_coords[1] <= 0:
            new_coords[1] = 1
            new_coords[0] = original_coords[0] - (original_coords[2] - WINDOW_WIDTH)
            new_coords[3] = original_coords[3] + abs(original_coords[1])
        elif original_coords[3] >= WINDOW_HEIGHT:
            new_coords[3] = WINDOW_HEIGHT - 1
            new_coords[1] = original_coords[1] - (original_coords[3] - WINDOW_HEIGHT)
            new_coords[0] = original_coords[0] - (original_coords[2] - WINDOW_WIDTH)
        else:
            new_coords[1] = original_coords[1]
            new_coords[0] = original_coords[0] - (original_coords[2] - WINDOW_WIDTH)
            new_coords[3] = original_coords[3]
        return new_coords
    # Wenn das Bild links anstößt, überprüfe, ob er auch noch nach oben oder unten anstößt
    elif original_coords[0] <= 0:
        new_coords[0] = 1
        if original_coords[1] <= 0:
            new_coords[1] = 1
            new_coords[2] = original_coords[2] + abs(original_coords[0])
            new_coords[3] = original_coords[3] + abs(original_coords[1])
        elif original_coords[3] >= WINDOW_HEIGHT:
            new_coords[3] = WINDOW_HEIGHT - 1
            new_coords[2] = original_coords[2] + abs(original_coords[0])
            new_coords[1] = original_coords[1] - (original_coords[3] - WINDOW_HEIGHT)
        else:
            new_coords[2] = original_coords[2] + abs(original_coords[0])
            new_coords[1] = original_coords[1]
            new_coords[3] = original_coords[3]
        return new_coords
    # Wenn das Bild oben anstößt, überprüfe, ob er auch noch nach links oder rechts anstößt
    elif original_coords[1] <= 0:
        new_coords[1] = 1
        if original_coords[0] <= 1:
            new_coords[0] = 1
            new_coords[2] = original_coords[2] + abs(original_coords[0])
            new_coords[3] = original_coords[3] + abs(original_coords[1])
        elif original_coords[2] > WINDOW_WIDTH:
            new_coords[2] = WINDOW_WIDTH - 1
            new_coords[0] = original_coords[0] - (original_coords[2] - WINDOW_WIDTH)
            new_coords[3] = original_coords[3] + abs(original_coords[1])
        else:
            new_coords[2] = original_coords[2]
            new_coords[0] = original_coords[0]
            new_coords[3] = original_coords[3] + abs(original_coords[1])
        return new_coords
    # Wenn das Bild unten anstößt, überprüfe, ob er auch noch nach links oder rechts anstößt
    elif original_coords[3] >= WINDOW_HEIGHT:
        new_coords[3] = WINDOW_HEIGHT - 1
        if original_coords[0] <= 1:
            new_coords[0] = 1
            new_coords[2] = original_coords[2] + abs(original_coords[0])
            new_coords[1] = original_coords[1] - (original_coords[3] - WINDOW_HEIGHT)
        elif original_coords[2] > WINDOW_WIDTH:
            new_coords[2] = WINDOW_WIDTH - 1
            new_coords[0] = original_coords[0] - (original_coords[2] - WINDOW_WIDTH)
            new_coords[3] = original_coords[3] - (original_coords[1] - WINDOW_HEIGHT)
        else:
            new_coords[2] = original_coords[2]
            new_coords[1] = original_coords[1] - (original_coords[3] - WINDOW_HEIGHT)
            new_coords[0] = original_coords[0]
        return new_coords
    else:
        return original_coords


def smoothMotion():
    new_coords = [0, 0, 0, 0, 0, [0, 0]]
    x1, y1, x2, y2, angle, center = (0, 0, 0, 0, 0, [0, 0])
    for i in range(MOVEMENT_SMOOTHNESS):
        x1 += coords_storage[0:MOVEMENT_SMOOTHNESS][i][0]
        y1 += coords_storage[0:MOVEMENT_SMOOTHNESS][i][1]
        x2 += coords_storage[0:MOVEMENT_SMOOTHNESS][i][2]
        y2 += coords_storage[0:MOVEMENT_SMOOTHNESS][i][3]
    new_coords[0] = round(x1 / MOVEMENT_SMOOTHNESS)
    new_coords[1] = round(y1 / MOVEMENT_SMOOTHNESS)
    new_coords[2] = round(x2 / MOVEMENT_SMOOTHNESS)
    new_coords[3] = round(y2 / MOVEMENT_SMOOTHNESS)
    for i in range(ROTATION_SMOOTHNESS):
        angle += coords_storage[0:ROTATION_SMOOTHNESS][i][4]
        center[0] += coords_storage[0:ROTATION_SMOOTHNESS][i][5][0]
        center[1] += coords_storage[0:ROTATION_SMOOTHNESS][i][5][1]
    average = round(angle / ROTATION_SMOOTHNESS)
    if abs(average) < ROTATION_THRESHOLD:
        if average > 0:
            average -= 1
        else:
            average += 1
    new_coords[4] = average
    new_coords[5][0] = round(center[0] / ROTATION_SMOOTHNESS)
    new_coords[5][1] = round(center[1] / ROTATION_SMOOTHNESS)
    del coords_storage[-1]
    return new_coords


def computeAngle(x1, x2, y1, y2):
    opposite = y2 - y1
    adjacent = abs(x2 - x1)
    hypotenuse = math.sqrt(math.pow(adjacent, 2) + math.pow(opposite, 2))
    angle = -1 * (round(math.degrees(opposite / hypotenuse)))
    return angle


def rotateImage(image, rotate_angle, centerpoint):
    rot_mat = cv2.getRotationMatrix2D(centerpoint, rotate_angle, 1.0)
    rotated_image = cv2.warpAffine(image, rot_mat, (WINDOW_WIDTH, WINDOW_HEIGHT), cv2.INTER_LINEAR)
    return rotated_image


with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        success, original_image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue  # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        original_image = cv2.cvtColor(cv2.flip(original_image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        original_image.flags.writeable = False
        results = face_detection.process(original_image)  # Draw the face detection annotations on the image.
        original_image.flags.writeable = True
        original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
        cropped_image = []
        faceWidth = 0
        faceHeight = 0
        if results.detections:
            for detection in results.detections:
                cropped_coords = computeCropping(detection)
                validated_coords = validateCropping(cropped_coords)
                coords_storage.insert(0, validated_coords)
                smoothed_coords = smoothMotion()
                rotated_image = rotateImage(original_image, smoothed_coords[4],
                                             smoothed_coords[5])
                cropped_image = rotated_image[smoothed_coords[1]:smoothed_coords[3],
                                smoothed_coords[0]:smoothed_coords[2]]
                mp_drawing.draw_detection(original_image, detection)
        try:
            cropped_image = cv2.resize(cropped_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        except:
            cropped_image = original_image[coords_storage[0][1]:coords_storage[0][3],
                            coords_storage[0][0]:coords_storage[0][2]]
            cropped_image = cv2.resize(cropped_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        cv2.imshow('Cropped Image', cropped_image)
        cv2.imshow('Original Image', original_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
