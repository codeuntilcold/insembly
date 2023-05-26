import cv2
import requests
import base64
import random


class Connector():
    def __init__(self):
        pass

    def send_data(self, image, output, output_aod):
        _, jpeg = cv2.imencode('.jpeg', image)
        base64_jpeg = base64.b64encode(jpeg)
        res = requests.post('http://127.0.0.1:5001/send-frame',
                      json={
                          "image": base64_jpeg.decode(),
                          "data": output,
                          "object": output_aod
                      })
        return res.json()['success']

    def test_webcam_stream(self):
        capture = cv2.VideoCapture('8_1_3.MOV')
        f = open('8_1_3.txt', 'r')
        lines = f.readlines()
        f.close()
        i = 0
        while True:
            _, frame = capture.read()
            if i < len(lines):
                model_output = f"{lines[i].strip()} {random.randrange(0, 99) / 100.0}"
                aod_output = f"{random.randint(0, 4)} {random.randrange(0, 99) / 100.0}"
                i += 1
                print(model_output)
            if not self.send_data(frame, model_output, aod_output):
                break


if __name__ == '__main__':
    conn = Connector()
    conn.test_webcam_stream()
