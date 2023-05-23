import cv2
import requests
import base64
import random


class Connector():
    def __init__(self):
        pass

    def send_data(self, image, output):
        _, jpeg = cv2.imencode('.jpeg', image)
        base64_jpeg = base64.b64encode(jpeg)
        requests.post('http://127.0.0.1:5001/send-frame',
                      json={
                          "image": base64_jpeg.decode(),
                          "data": output
                      })

    def test_webcam_stream(self):
        capture = cv2.VideoCapture('5_4_4.MOV')
        f = open('5_4_4.txt', 'r')
        lines = f.readlines()
        f.close()
        i = 0
        while True:
            _, frame = capture.read()
            if i < len(lines):
                model_output = f"{lines[i].strip()} {random.randrange(0, 99) / 100.0}"
                i += 1
                print(model_output)
            self.send_data(frame, model_output)


if __name__ == '__main__':
    conn = Connector()
    conn.test_webcam_stream()
