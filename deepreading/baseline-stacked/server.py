from flask import Flask, request
from flask_cors import CORS
from waitress import serve

from tensorflow.keras.models import load_model

from ..shared import util, variables

app = Flask(__name__)
cors = CORS(app)

alphabet = list(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,-()/"
)  # %:;&# '\x00' character, i.e., ord(0) to label concatenations.
alphabet.insert(0, chr(0))
model = load_model('./deepreading/baseline-stacked/model/deepwriting_model.hdf5')


@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    if len(input_json['word_stroke']) != 0:
        model_input = util.parse_json(input_json)
        model_output = model.predict(model_input)
        result = util.process_result(model_output, alphabet)
        return {'result': result}
    else:
        return {'result': ''}


def main():
    serve(app, host='0.0.0.0', port=variables.BASELINE_PORT)


if __name__ == "__main__":
    main()
