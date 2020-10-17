from flask import Flask, request
from flask_cors import CORS
from waitress import serve

from tensorflow.keras.layers import Input
from tensorflow.keras.models import load_model, Model

from sklearn.preprocessing import LabelEncoder

from ..shared import util, variables
from os import path
import numpy as np

alphabet = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,;:!?-+*()[]&/ \"#")  # %:;&#
alphabet.insert(0, chr(0))  # '\x00' character, i.e., ord(0) to label concatenate
alphabet.insert(1, '\t')  # start of sequence
alphabet.insert(2, '\n')  # end of sequence

max_decoder_seq_length = 100

encoder_space = 512
decoder_space = encoder_space * 2

model = load_model('./deepreading/seq2seq/model/best_model_seq2seq_512.hdf5')


# Encoder Model
encoder_model = Model(model.get_layer('encoder_input').output, [model.get_layer('merge_h').output, model.get_layer('merge_c').output])

# Decoder Model
decoder_state_input_h = Input(decoder_space, )
decoder_state_input_c = Input(decoder_space, )

decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]

decoder_outputs, decoder_state_h, decoder_state_c = model.get_layer('decoder')(
    model.get_layer('masking_decoder').output,
    initial_state=decoder_state_inputs
)

decoder_states = [decoder_state_h, decoder_state_h]
decoder_outputs = model.get_layer('dense_decoder')(decoder_outputs)

decoder_model = Model(
    [model.get_layer('decoder_input').output] + decoder_state_inputs,
    [decoder_outputs] + decoder_states
)


# check out https://keras.io/examples/lstm_seq2seq/
def inference(model_input):
    # Inference

    # label_encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(alphabet)

    states_value = encoder_model.predict(model_input)

    # Generate Target Sequence
    target_seq = np.zeros((1, 1, len(alphabet)))
    target_seq[0, 0, label_encoder.transform(['\t'])[0]] = 1

    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = label_encoder.inverse_transform([sampled_token_index])[0]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '\n' or len(decoded_sentence) > max_decoder_seq_length):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, len(alphabet)))
        target_seq[0, 0, sampled_token_index] = 1.

        # Update states
        states_value = [h, c]

    return decoded_sentence


app = Flask(__name__)
cors = CORS(app)
@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    model_input = util.parse_json(input_json)
    result = inference(model_input)
    return {"result": result}


def main():
    serve(app, host='0.0.0.0', port=variables.SEQ2SEQ_PORT)


if __name__ == "__main__":
    main()