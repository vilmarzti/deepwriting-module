from flask import Flask, request
from flask_cors import CORS

from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

from ..shared import util
import numpy as np

app = Flask(__name__)
cors = CORS(app)

alphabet = list(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,-()/"
)  # %:;&# '\x00' character, i.e., ord(0) to label concatenations.
alphabet.insert(0, chr(0))
model = load_model('./keras/baseline/model/best_model_512.hdf5')


@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    if len(input_json['word_stroke']) != 0:
        model_input = util.parse_json(input_json)
        model_output = model.predict(model_input)
        result = process_result(model_output, alphabet)
        return {'result': result}
    else:
        return {'result': ''}



def process_result(result, alphabet):
    bow_positions = np.where(result[2] > 0.8)[1]
    eoc_positions = np.where(result[1] > 0.8)[1]

    char_prediction = result[0][0]
    argmax_char = np.argmax(char_prediction, 1)

    char_label_encoder = LabelEncoder()
    char_label_encoder.fit(alphabet)

    chars = char_label_encoder.inverse_transform(argmax_char)
    char_probs = [(char_prediction[index, value],) for index, value in enumerate(argmax_char)]

    chars = [(c,) for c in chars]
    chars = [chars[i] + char_probs[i] for i in range(len(chars))]
    chars = [chars[p] + ('bow',) if p in bow_positions else chars[p] for p in range(len(chars))]
    chars = [chars[p] + ('eoc',) if p in eoc_positions else chars[p] for p in range(len(chars))]

    if 'bow' not in chars[0]:
        chars[0] = chars[0] + ('bow',)
    if 'eoc' not in chars[-1]:
        chars[-1] = chars[-1] + ('eoc',)

    chars_collapsed = []
    history = []
    for idx, char in enumerate(chars):
        if 'eoc' in char:
            if history:
                # Find most probable character based on their probability
                probability_dict = {}
                for h in history:
                    if h[0] in probability_dict:
                        probability_dict[h[0]] + h[1]
                    else:
                        probability_dict[h[0]] = h[1]

                #most_common = max(set(history), key=history.count)
                most_common = max(probability_dict, key=probability_dict.get)
                chars_collapsed.append(most_common)
            history = []
        elif 'bow' in char and idx != 0:
            chars_collapsed.append(" ")
        else:
            history.append(char)
    return "".join(chars_collapsed)


def main():
    app.run(port=5000)


if __name__ == "__main__":
    main()
