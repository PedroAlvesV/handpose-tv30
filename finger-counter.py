import cv2
import time
import os
import HandTrackingModule as htm

def indexOf(finger, distance=0):
    if finger < 1 or finger > 5 or distance < 0 or distance > 3: return -1
    return (finger*4)-distance

def dist(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
def is_closed(finger):
    if finger == 1:
        # d1 = tip of thumb to pinky knuckle
        # d2 = index finger knuckle to pinky knuckle
        d1 = dist(lmList[4][1], lmList[4][2], lmList[17][1], lmList[17][2])
        d2 = dist(lmList[5][1], lmList[5][2], lmList[17][1], lmList[17][2])
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

folderPath = "FingerImages"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    # print(f'{folderPath}/{imPath}')
    overlayList.append(image)

print(len(overlayList))
pTime = 0

detector = htm.handDetector(maxHands=1, detectionCon=0.75)

tipIds = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # print(lmList)

    if len(lmList) != 0:
        fingers = []

        # Thumb
        is_right_hand = lmList[1][1] > lmList[0][1]
    
        if is_right_hand:
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 2][1]:
                fingers.append(True)
            else:
                fingers.append(False)
        else: 
            if lmList[tipIds[0]][1] < lmList[tipIds[0] - 2][1]:
                fingers.append(True)
            else:
                fingers.append(False)


        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(True)
            else:
                fingers.append(False)

        #print(fingers)
        totalFingers = fingers.count(True)
        #print(totalFingers)

        fingers2 = [is_closed(1), is_closed(2), is_closed(3), is_closed(4), is_closed(5)]
        totalFingers = fingers2.count(False)
        print(fingers2)

        #h, w, c = overlayList[totalFingers - 1].shape
        #img[0:h, 0:w] = overlayList[totalFingers - 1]

        cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(totalFingers), (45, 375), cv2.FONT_HERSHEY_PLAIN,
                    10, (255, 0, 0), 25)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()