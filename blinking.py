import time
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector


class Blinking:

    capture = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=1)
    x1, y1 = 0, 0
    x2, y2 = 100, 100

    while True:
        success, img = capture.read()
        img, faces = detector.findFaceMesh(img)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 5)


        img = cv2.resize(img, (800, 600))
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        if cv2.waitKey(1) == ord('q'):
            break

if __name__ == "__main__":
    Blinking()