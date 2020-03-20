from flask import Flask, request
from flask_cors import CORS

from tensorflow.keras.layers import LSTM, Input, Dense, TimeDistributed, Masking, Bidirectional, Concatenate
from tensorflow.keras.models import load_model, Model

from sklearn.preprocessing import LabelEncoder

from ..shared import util, variables
from os import path
import numpy as np


app = Flask(__name__)
cors = CORS(app)

alphabet = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,;:!?-+*()[]&/ \"#")  # %:;&#
alphabet.insert(0, chr(0))  # '\x00' character, i.e., ord(0) to label concatenate
alphabet.insert(1, '\t')  # start of sequence
alphabet.insert(2, '\n')  # end of sequence


encoder_space = 256
decoder_space = encoder_space * 2

model = load_model(path.join(variables.WORKSPACEFOLDER, 'keras/seq2seq/model/best_model_seq2seq_256.hdf5'))


@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    model_input = util.parse_json(input_json)
    result = inference(model_input)
    return result


# check out https://keras.io/examples/lstm_seq2seq/
def inference(model_input):
    # Encoder Model
    encoder_model = Model(model.get_layer('encoder_input').output, [model.get_layer('merge_h').output, model.get_layer('merge_c').output])

    # Decoder Model
    decoder_state_input_h = Input(decoder_space, )
    decoder_state_input_c = Input(decoder_space, )

    decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]

    decoder_outputs, decoder_state_h, decoder_state_c = model.get_layer('decoder')(
        model.get_layer('decoder_input').output,
        initial_state=decoder_state_inputs
    )

    decoder_states = [decoder_state_h, decoder_state_h]
    decoder_outputs = model.get_layer('dense_decoder')(decoder_outputs)

    # Inference

    # label_encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(alphabet)


    state_value = encoder_model.predict(model_input)

    # Generate Target Sequence
    target_seq = np.zeros((1, 1, len(alphabet)))
    target_seq[0, 0, label_encoder.transform(['\t'])[0]] = 1
    return "T"


if __name__ == '__main__':
    app.run(port=5000)
