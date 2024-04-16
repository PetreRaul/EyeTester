import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector


class FaceDetection:
    def init(self):
        self.capture = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)

    def startdetection(self):
        while True:
            success, img = self.capture.read()
            img, faces = self.detector.findFaceMesh(img, False)

            if faces:
                face = faces[0]
                pointLeft = face[145]
                pointRight = face[374]

                cv2.line(img, pointLeft, pointRight, (0, 200, 0), 3)
                cv2.circle(img, pointLeft, 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)

                w, = self.detector.findDistance(pointLeft, pointRight)
                print(w)

                W  = 6.3
                # d = 50
                # f = (wd)/W
                # print(f)
                f = 840
                d = (W*f)/w
                print(d)


            cv2.imshow("Image", img)
            if cv2.waitKey(1) == ord('q'):  # Press 'q' to quit
                break

# if __name__ == "main":
#     face_detector = FaceDetection()
#     face_detector.start_detection()