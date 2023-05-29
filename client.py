from flask import Flask, render_template, Response, request, jsonify
import requests
import base64
import time
import os
import json
from flask_socketio import SocketIO

ACTIONS = [
    "open phone box",
    "take out phone",
    "take out instruction paper",
    "take out earphones",
    "take out charger",
    "put in charger",
    "put in earphones",
    "put in instruction paper",
    "inspect phone",
    "put in phone",
    "close phone box",
    "no action"   
]
FPS = 24.0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


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
        for action in content['report']:
            action['action_name'] = ACTIONS[action['action_id']]
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
        time.sleep(1 / FPS)


@app.route('/label_feed', methods=['GET'])
def label_feed():
    return Response(get_label(), mimetype='text/event-stream')


def get_label():
    while True:
        try:
            response_c = requests.get('http://127.0.0.1:5001/label')
            action = bytes(str(response_c.json()['action']), encoding='utf-8')
            prob = bytes(str(response_c.json()['prob']), encoding='utf-8')
            object = bytes(str(response_c.json()['object']), encoding='utf-8')
        except Exception as e:
            app.logger.error(e)
            action, prob, object = b'11', b'0.0', b'-1'
        yield b'data: ' + action + b' ' + prob + b' ' + object + b'\n\n'
        time.sleep(1 / FPS)


@app.route('/state-changed', methods=['POST'])
def state_changed():
    socketio.emit('state-changed', request.get_json())
    return jsonify(success=True)

@app.route('/missed-actions', methods=['POST'])
def missed_actions():
    socketio.emit('missed-actions', request.get_json())
    return jsonify(success=True)

@app.route('/log', methods=['POST'])
def add_log():
    socketio.emit('add-log', request.get_json())
    return jsonify(success=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
