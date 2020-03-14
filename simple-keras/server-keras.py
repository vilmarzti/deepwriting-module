from flask import Flask, request
from flask_cors import CORS

from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

import numpy as np

app = Flask(__name__)
cors = CORS(app)

alphabet = list(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,-()/"
)  # %:;&# '\x00' character, i.e., ord(0) to label concatenations.
alphabet.insert(0, chr(0))


@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    model = load_model('./model/best_model_512.hdf5')
    model_input = parse_json(input_json)
    model_output = model.predict(model_input)
    result = process_result(model_output, alphabet)
    return result


def parse_json(input_json):
    strokes = input_json['word_stroke']
    model_input = []

    # read strokes
    for stroke in strokes:
        elem = [stroke['x'], stroke['y'], stroke['ev']]
        model_input.append(elem)
    model_input = np.array(model_input)

    # Normalize the strokes
    # x_normalized = (model_input[:, 0] - np.mean(model_input[:, 0])) / np.linalg.norm(model_input[:, 0])
    # y_normalized = (model_input[:, 1] - np.mean(model_input[:, 0])) / np.linalg.norm(model_input[:, 1])
    # model_input = np.array([x_normalized, y_normalized, model_input[:, 2]]).transpose()

    # model_input = np.array([model_input[:, 0].astype('float'), model_input[:, 1].astype('float'), model_input[:, 2]]).transpose()

    x_normalized = standartize_vector(calculate_diff(model_input[:, 0]))
    y_normalized = standartize_vector(calculate_diff(model_input[:, 1]))
    model_input = np.array([x_normalized, y_normalized, model_input[1:, 2]]).transpose()

    # Add other dimension for model to predict
    model_input = np.expand_dims(model_input, axis=0)
    return model_input


def calculate_diff(vector):
    vector = np.array(vector).astype('float')
    vector = np.diff(vector)
    return vector


def scale_to_zero_one(vector):
    minimum = np.min(vector)
    maximum = np.max(vector)
    vector = (vector - minimum) / (maximum - minimum)
    return vector, minimum


def standartize_vector(vector):
    mean = np.mean(vector)
    std = np.std(vector)
    vector = (vector - mean) / std
    return vector


def process_result(result, alphabet):
    bow_positions = np.where(result[2] > 0.8)[1]
    eoc_positions = np.where(result[1] > 0.8)[1]
    char_prediction = result[0][0]
    argmax_char = np.argmax(char_prediction, 1)

    char_label_encoder = LabelEncoder()
    char_label_encoder.fit(alphabet)

    chars = char_label_encoder.inverse_transform(argmax_char)
    chars = [(c,) for c in chars]
    chars = [chars[p] + ('eoc',) if p in eoc_positions else chars[p] for p in range(len(chars))]
    chars = [chars[p] + ('bow',) if p in bow_positions else chars[p] for p in range(len(chars))]

    print(chars)
    chars_collapsed = []
    history = []
    for idx, char in enumerate(chars):
        if len(char) == 1:
            history.append(char[0])
        if 'eoc' in char:
            most_common = max(set(history), key=history.count)
            chars_collapsed.append(most_common)
            history = []
        if 'bow' in char and idx != 0:
            chars_collapsed.append(" ")
    return "".join(chars_collapsed)


if __name__ == '__main__':
    app.run(port=5000)
