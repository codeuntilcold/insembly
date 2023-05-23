from flask import Flask, render_template, Response
import requests
import base64

app = Flask(__name__)

total_pixel_count = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/report')
def report():
    return render_template('report.html')


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/label_feed', methods=['GET'])
def label_feed():
    return Response(get_label(), mimetype='text/event-stream')


def get_frame():
    while True:
        try:
            response_c = requests.get('http://127.0.0.1:5001/frame')
            frame_data = response_c.json()['frame']
            jpeg_original = base64.b64decode(frame_data)
        except Exception as e:
            app.logger.error(e)
            jpeg_original = b''

        # Yield frame with pixel count
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_original + b'\r\n')


def get_label():
    while True:
        try:
            response_c = requests.get('http://127.0.0.1:5001/label')
            label = bytes(response_c.json()['label'], encoding='utf-8')
            prob = bytes(response_c.json()['prob'], encoding='utf-8')
        except Exception as e:
            app.logger.error(e)
            label, prob = b"-1", b"0.0"

        yield b'data: ' + label + b' ' + prob + b'\n\n'


if __name__ == '__main__':
    app.run(debug=True)
