import cv2
import time
import HandTrackingModule as htm
from sys import argv
import paho.mqtt.client as mqtt

DEBUG = False
QUIET = False

if len(argv) < 2 or argv[1][0] == '-':
    print("usage: python3 handpose.py <max-hands> [-d | --debug]")
    exit()

MAX_HANDS = int(argv[1])
if MAX_HANDS < 1:
    print("'max-hands' must be at least 1")
    exit()

if len(argv) > 2:
    DEBUG = argv[2] == '-d' or argv[2] == '--debug'
    QUIET = argv[2] == '-q' or argv[2] == '--quiet'

broker_address = "localhost" #input("Broker address: ")

print("Attempting connection...")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client()
client.on_connect = on_connect

client.connect(broker_address, 1883, 60)

print(f"Connected to {broker_address}:1883")

def indexOf(finger, distance=0):
    if finger < 1 or finger > 5 or distance < 0 or distance > 3: return -1
    return (finger*4)-distance

def dist(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
def is_closed(finger, lmList):
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

detector = htm.handDetector(maxHands=MAX_HANDS, detectionCon=0.75)

poses = []

__UNDEF = "undefined"

# 0 fingers pose
p = {"FIST": [False]*5}
poses.append(p)

# 1 finger poses
p = {
    "POINT": [False, True, False, False, False],
    "FIST": [True, False, False, False, False]
}
poses.append(p)

# 2 fingers poses
p = {
    "PEACE": [False, True, True, False, False],
    "ROCK": [False, True, False, False, True],
    "SHAKA": [True, False, False, False, True],
    "LOSER": [True, True, False, False, False]
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
    return __UNDEF

INTERVAL = 0.4
    
timer = time.time()

hands = dict()
last_results = dict()
for i in range(MAX_HANDS):
    hands[i] = dict()
    hands[i][__UNDEF] = 0
    for p in poses:
        for k in p:
            hands[i][k] = 0
    last_results[i] = __UNDEF

def reset_hand(handNo):
    hand = hands[handNo]
    for pose in hand:
        hand[pose] = 0

def evaluate(g):
    max_key = max(g, key=g.get)
    return max_key

def read_hand(img, handNo=0):
    
    lmList = detector.findPosition(img, handNo=handNo, draw=False)

    if len(lmList) != 0:
        
        fingers = []
        for i in range(1,6):
            fingers.append(not is_closed(i, lmList))
        hands[handNo][getPose(fingers)] += 1
        #print(fingers, getPose(fingers))

while True:

    client.loop(timeout=0.05)

    success, img = cap.read()
    numHands, img = detector.findHands(img)

    for i in range(numHands):
        read_hand(img, handNo=i)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    t = time.time() - timer
    
    if t > INTERVAL:

        for i in range(numHands):
            hand = hands[i]
            result = evaluate(hand)
            if DEBUG:
                print(result)
            if result != __UNDEF and result != last_results[i]:
                client.publish("handpose_recog", result)
                if not QUIET:
                    print(f"-> Published '{result}'")
                last_results[i] = result
            reset_hand(i)
            timer += t

    if DEBUG:
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q'):
            break

cap.release()
cv2.destroyAllWindows()
