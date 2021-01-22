from flask import Flask, request
from flask_cors import CORS
from waitress import serve

from tensorflow.keras.layers import Input
from tensorflow.keras.models import load_model, Model

from sklearn.preprocessing import LabelEncoder

from ..shared import util, variables
import numpy as np
import copy

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
    num_decoded_chars = 0
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = label_encoder.inverse_transform([sampled_token_index])[0]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '\n' or num_decoded_chars > max_decoder_seq_length):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, len(alphabet)))
        target_seq[0, 0, sampled_token_index] = 1.

        # Update states
        states_value = [h, c]
        num_decoded_chars += 1

    return decoded_sentence


# Class used for beam search
class Beam(object):
    max_length = 20
    alpha = 0.7

    def __init__(self, probability, decoded_sentence, state, stopping_condition=False):
        self.probabilities = []
        self.probabilities.append(probability)
        self.decoded_sentence = decoded_sentence
        self.state = state
        self.stopping_condition = stopping_condition
        self.num_decoded_chars = 0

    def append(self, probablitiy, char, state):
        self.probabilities.append(probablitiy)
        self.decoded_sentence = self.decoded_sentence + char
        self.state = state
        self.num_decoded_chars += 1
        if(self.num_decoded_chars >= self.max_length or char == "\n"):
            self.stopping_condition = True

    @property
    def log_probability(self):
        return np.power(1.0 / self.num_decoded_chars, self.alpha) * sum([np.log(prob) for prob in self.probabilities])
        # return sum([np.log(prob) for prob in self.probabilities])

    @property
    def probability(self):
        return np.prod(self.probabilities)

    @property
    def char(self):
        return self.decoded_sentence[-1]

    def target_sequence(self, position):
        target_seq = np.zeros([1, 1, len(alphabet)])
        target_seq[0, 0, position] = 1
        return target_seq


def beam_search(model_input, beam_width=5):
    # label encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(alphabet)

    # generate the output of the encoder
    states_value = encoder_model.predict(model_input)

    # Generate starting Beam
    beam = Beam(1.0, "\t", states_value)
    beams = [beam]

    # beam search
    selected_beams = []
    while len(selected_beams) < beam_width:
        new_beams = []
        for beam in beams:
            # Don't expand on already finished beam
            if beam.stopping_condition:
                continue

            # get the target sequence
            position = label_encoder.transform([beam.char])
            target_seq = beam.target_sequence(position)

            # compute probabilities
            output_tokens, h, c = decoder_model.predict([target_seq] + beam.state)

            states = [h, c]

            # For each probability add a new entry into the list
            probabilities = output_tokens[0, 0, :]
            for index, prob in enumerate(probabilities):
                char = label_encoder.inverse_transform([index])[0]

                # create a new copy of beam and append it to the list
                beam_copy = copy.deepcopy(beam)
                beam_copy.append(prob, char, states)
                new_beams.append(beam_copy)
                
        # Sort list descendetly based on their probability
        new_beams.sort(reverse=True, key=lambda beam: beam.log_probability)

        # extract top beams
        beams = new_beams[:beam_width]

        # if one beam in top five is finished, select them
        for beam in beams:
            if beam.stopping_condition: 
                selected_beams.append(beam)

        # cut selected beams to length of beam_width
        selected_beams = selected_beams[:beam_width]

        # sort selected beams
        selected_beams.sort(reverse=True, key=lambda beam: beam.log_probability)

    return selected_beams


def beams_to_result(beams):
    result_dict = {}
    for beam in beams:
        # remove starting and ending tokens
        result_string = beam.decoded_sentence[1:-1]
        result_dict[result_string] = beam.probability
    return result_dict


app = Flask(__name__)
cors = CORS(app)


@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path')
def evaluate(u_path):
    input_json = request.json
    model_input, beam_width = util.parse_json(input_json)

    # greedy algorithm
    # result = inference(model_input)

    # beam search
    beams = beam_search(model_input, beam_width)
    result = beams_to_result(beams)
    return result


def main():
    serve(app, host='0.0.0.0', port=variables.SEQ2SEQ_PORT, threads=100, url_scheme="https")


if __name__ == "__main__":
    main()
