import time
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector


class Blinking:


    def start_exercise_2(self):
        self.is_first_ex_playing = True
        self.capture_exercise_2 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        #self.capture_exercise_2= cv2.VideoCapture(0)
        detector = FaceMeshDetector(maxFaces=1)

        id_list = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
        ratio_list = []
        blink_counter = 0
        counter = False
        last_blink = time.time()

        while True:
            success, img = self.capture_exercise_2.read()
            if success:
                img_with_detections = img.copy()
                img_with_detections, faces = detector.findFaceMesh(img_with_detections, draw=False)
                current_time = time.time()
                time_since_last_blink = current_time - last_blink
                if faces:
                    face = faces[0]
                    for id in id_list:
                        cv2.circle(img, face[id], 5, (255, 255, 255), cv2.FILLED)

                    left_eye_up_position = face[159]
                    left_eye_down_position = face[23]
                    left_eye_left_position = face[130]
                    left_eye_right_position = face[243]

                    vertical_length, _ = detector.findDistance(left_eye_up_position, left_eye_down_position)
                    horizontal_length, _ = detector.findDistance(left_eye_left_position, left_eye_right_position)

                    ratio = int((vertical_length / horizontal_length) * 100)
                    ratio_list.append(ratio)

                    if len(ratio_list) > 3:
                        ratio_list.pop(0)
                    ratio_average = sum(ratio_list) / len(ratio_list)
                    print(ratio_average)

                    if ratio_average < 35 and counter == 0:
                        blink_counter += 1
                        counter = 1
                        last_blink = current_time
                    if counter != 0:
                        counter += 1
                        if counter > 10:
                            counter = 0

                if time_since_last_blink > 5:
                    cvzone.putTextRect(img_with_detections, 'Please blink', (20, 150), scale=1.5, thickness=2, colorR=(255, 0, 0))

            frame = cv2.cvtColor(img_with_detections, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.exercise_2.setPixmap(QPixmap.fromImage(q_img))

            if cv2.waitKey(1) == ord('q'):
                break

if __name__ == "__main__":
    Blinking()