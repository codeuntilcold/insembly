from dataclasses import dataclass
from flask import Flask, jsonify, request
import requests
import logging
from action_transition_graph.graph import Bucket, TransitionGraph  # noqa: E402


@dataclass
class AppState:
    label: int
    prob: float
    image: str


app = Flask(__name__)
# app.logger.setLevel("ERROR")
# logging.getLogger('werkzeug').setLevel(logging.ERROR)

state = AppState(-1, 0.0, "")
bucket = Bucket(stream=None, radius=16)
graph = TransitionGraph(hardcode_graph=False, save_report_as_files=True)


@app.route('/send-frame', methods=['POST'])
def sendframe():
    global state
    data = request.get_json()

    new_state, prev_conf, conf = bucket.drip(data['data'])
    result = graph.update_state(new_state, prev_conf)

    if result.has_changed:
        requests.post('http://127.0.0.1:5000/state-changed', json={
            'label': result.state,
            'is_mistake': result.is_mistake
        })

    state.state = new_state
    state.prob = conf
    state.image = data['image']
    return jsonify(success=True)


@app.route('/frame')
def frame():
    return jsonify(frame=state.image)


@app.route('/label')
def label():
    return jsonify(label=state.label, prob=state.prob)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
