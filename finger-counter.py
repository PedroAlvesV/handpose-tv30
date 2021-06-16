import cv2
import time
import HandTrackingModule as htm

def indexOf(finger, distance=0):
    if finger < 1 or finger > 5 or distance < 0 or distance > 3: return -1
    return (finger*4)-distance

def dist(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
def is_closed(finger):
    if finger == 1:
        # d1 = tip of thumb to ring finger knuckle
        # d2 = tip of thumb to thumb knuckle
        d1 = dist(lmList[4][1], lmList[4][2], lmList[13][1], lmList[13][2])
        d2 = dist(lmList[4][1], lmList[4][2], lmList[2][1], lmList[2][2])
    else:
        # d1 = tip to wrist 
        # d2 = proximal joint to wrist
        d1 = dist(lmList[indexOf(finger)][1], lmList[indexOf(finger)][2], lmList[0][1], lmList[0][2])
        d2 = dist(lmList[indexOf(finger, 2)][1], lmList[indexOf(finger, 2)][2], lmList[0][1], lmList[0][2])
    return d1 < d2

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

detector = htm.handDetector(maxHands=1, detectionCon=0.75)

poses = []

# 0 fingers pose
p = {"FIST": [False]*5}
poses.append(p)

# 1 finger poses
p = {
    "POINT": [False, True, False, False, False],
    "THUMBS": [True, False, False, False, False]
}
poses.append(p)

# 2 fingers poses
p = {
    "PEACE": [False, True, True, False, False],
    "ROCK": [False, True, False, False, True],
    "SHAKA": [True, False, False, False, True]
}
poses.append(p)

# 3 fingers poses
p = {
    "THREE": [False, True, True, True, False],
    "LOVE": [True, True, False, False, True]
}
poses.append(p)

# 4 fingers poses
p = {"FOUR": [False, True, True, True, True]}
poses.append(p)

# 5 fingers poses
p = {"OPEN": [True]*5}
poses.append(p)

def getPose(fingers):
    totalFingers = fingers.count(True)
    for pose in poses[totalFingers]:
        if poses[totalFingers][pose] == fingers:
            return pose
    return "UNDEF"

# poderia codificar em binário, também, e usar a própria sequência como chave de dicionário. ex.: "01000" como "POINT"

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        
        fingers = []
        for i in range(1,6):
            fingers.append(not is_closed(i))
        print(fingers, getPose(fingers))

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()