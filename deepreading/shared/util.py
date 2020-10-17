import numpy as np
from sklearn.preprocessing import LabelEncoder
import numpy as np

def parse_json(input_json):
    strokes = input_json['word_stroke']

    # read strokes
    model_input = []
    for stroke in strokes:
        elem = [stroke['x'], stroke['y'], stroke['ev']]
        model_input.append(elem)

    model_input = np.array(model_input)
    #model_input = scale_to_zero_one(model_input)
    #model_input = translate_to_origin(model_input)
    model_input = calculate_diff(model_input)
    model_input = standartize_vector(model_input)

    # Add new dimension for batch_size
    model_input = np.expand_dims(model_input, axis=0)
    return model_input


def calculate_diff(model_input):
    source = np.vstack((model_input[0], model_input))
    model_input = np.diff(source, axis=0)
    return model_input


def translate_to_origin(model_input):
    origin = np.append(model_input[0, [0, 1]], [0])
    return model_input - origin


def scale_to_zero_one(model_input):
    minimum = np.min(model_input, axis=0)
    maximum = np.max(model_input, axis=0)
    model_input = (model_input - minimum) / (maximum - minimum)
    return model_input


def normalize_vector(vector):
    mean = np.mean(vector)
    return vector - mean


def standartize_vector(model_input):
    mean = np.mean(model_input, axis=0)
    std = np.std(model_input, axis=0)
    mean[2] = 0.0
    std[2] = 1.0
    model_input = (model_input - mean) / std
    return model_input 


def process_result(result, alphabet):
    eow_positions = np.where(result[2] > 0.8)[1]
    eoc_positions = np.where(result[1] > 0.8)[1]

    char_prediction = result[0][0]
    argmax_char = np.argmax(char_prediction, 1)

    char_label_encoder = LabelEncoder()
    char_label_encoder.fit(alphabet)

    chars = char_label_encoder.inverse_transform(argmax_char)
    char_probs = [(char_prediction[index, value],) for index, value in enumerate(argmax_char)]

    chars = [(c,) for c in chars]
    chars = [chars[i] + char_probs[i] for i in range(len(chars))]
    chars = [chars[p] + ('eow',) if p in eow_positions else chars[p] for p in range(len(chars))]
    chars = [chars[p] + ('eoc',) if p in eoc_positions else chars[p] for p in range(len(chars))]

    if 'eoc' not in chars[-1]:
        chars[-1] = chars[-1] + ('eoc',)

    if 'eow' not in chars[-1]:
        chars[-1] = chars[-1] + ('eow',)

    chars_collapsed = []
    history = []
    for idx, char in enumerate(chars):
        if 'eoc' not in char and 'eow' not in char:
            history.append(char)

        if 'eoc' in char or 'eow' in char:
            if history:
                # Find most probable character based on their probability
                probability_dict = {}
                for h in history:
                    if h[0] in probability_dict:
                        probability_dict[h[0]] += h[1]
                    else:
                        probability_dict[h[0]] = h[1]

                #most_common = max(set(history), key=history.count)
                most_common = max(probability_dict, key=probability_dict.get)
                chars_collapsed.append(most_common)
            history = []
        
        if 'eow' in char:
            chars_collapsed.append(" ")

    return "".join(chars_collapsed)

