from dataclasses import dataclass
from flask import Flask, jsonify, request
import requests
import logging
import sys
sys.path.append("D:\\Study document\\Luận văn\\tsn-online-demo")
from action_transition_graph.graph import Bucket, TransitionGraph  # noqa: E402


@dataclass
class AppState:
    action: int
    prob: float
    image: str
    object: int


app = Flask(__name__)
app.logger.setLevel("ERROR")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

state = AppState(-1, 0.0, "", -1)
bucket = Bucket(stream=None, radius=8)
graph = TransitionGraph(hardcode_graph=True, save_report_as_files=True)


@app.route('/send-frame', methods=['POST'])
def sendframe():
    global state
    data = request.get_json()

    try:
        new_state, prev_conf, conf = bucket.drip(data['data'])
        result = graph.update_state(new_state, prev_conf)
    except Exception as e:
        app.logger.error(e)
        return jsonify(success=False)

    if result.has_changed:
        requests.post('http://127.0.0.1:5000/state-changed', json={
            'label': result.state,
            'is_mistake': result.is_mistake
        })

        if result.is_mistake and len(result.missed_steps):
            requests.post('http://127.0.0.1:5000/missed-actions', json={
                'actions': list(result.missed_steps)
            })
    
    # requests.post('http://127.0.0.1:5000/log', json={
    #     'state': new_state,
    #     'prob': conf
    # })

    raw_data = data['data'].split(' ')
    state.action = int(raw_data[0])
    state.prob = float(raw_data[1])
    state.image = data['image']
    state.object = data['object'].split("@")[0]
    return jsonify(success=True)


@app.route('/frame')
def frame():
    return jsonify(frame=state.image)


@app.route('/label')
def label():
    return jsonify(action=state.action, prob=state.prob, object=state.object)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
