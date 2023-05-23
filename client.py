from flask import Flask, render_template, Response, request
import requests
import base64
import time
import os
import json
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

total_pixel_count = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/report')
def report():
    files = os.listdir('report')
    files = [file.replace('.txt', '') for file in files]
    return render_template('reports.html', files=files)


@app.route('/report/<id>')
def each_report(id):
    with open(f'report/{id}.txt', 'r') as f:
        content = f.read()
        content = json.loads(content)
        return render_template('report.html', content=content['report'], id=id)


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


def get_frame():
    while True:
        try:
            response_c = requests.get('http://127.0.0.1:5001/frame')
            frame_data = response_c.json()['frame']
            jpeg_original = base64.b64decode(frame_data)
        except Exception as e:
            app.logger.error(e)
            jpeg_original = b''
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_original + b'\r\n')
        time.sleep(1 / 24.0)


@app.route('/label_feed', methods=['GET'])
def label_feed():
    return Response(get_label(), mimetype='text/event-stream')


def get_label():
    while True:
        try:
            response_c = requests.get('http://127.0.0.1:5001/label')
            label = bytes(str(response_c.json()['label']), encoding='utf-8')
            prob = bytes(str(response_c.json()['prob']), encoding='utf-8')
        except Exception as e:
            app.logger.error(e)
            label, prob = b'11', b'0.0'
        yield b'data: ' + label + b' ' + prob + b'\n\n'
        time.sleep(1 / 24.0)


@app.route('/state-changed', methods=['POST'])
def state_changed():
    socketio.emit('state-changed', request.get_json())


if __name__ == '__main__':
    socketio.run(app, debug=True)
