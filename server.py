from flask import Flask, jsonify, request
import logging
from action_transition_graph.graph import Bucket, TransitionGraph  # noqa: E402

app = Flask(__name__)
app.logger.setLevel("ERROR")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

state = {
    "label": "-1",
    "prob" : "0.0",
    "image" : ""
}


def gen():
    global state
    while True:
        message = f"{state['label']} {state['prob']}"
        yield message


bucket = Bucket(stream=gen(), radius=16)
graph = TransitionGraph(hardcode_graph=False, save_report_as_files=True)


@app.route('/send-frame', methods=['POST'])
def sendframe():
    global state
    data = request.get_json()

    new_state, prev_conf, conf = bucket.drip(data['data'])
    app.logger.error(f"RECEIVED: {new_state}")

    curstate = graph.update_state(new_state, prev_conf)
    app.logger.error(f"CURRENT: {curstate}")

    state['label'], state['prob'] = str(curstate), str(conf)
    state['image'] = data["image"]

    # app.logger.info(state['label'])
    # app.logger.info(state['prob'])

    return jsonify(success=True)


@app.route('/frame')
def frame():
    global state
    return jsonify(frame=state["image"])


@app.route('/label')
def label():
    global state
    return jsonify(label=state['label'], prob=state['prob'])


if __name__ == '__main__':
    app.run(port=5001, debug=True)
