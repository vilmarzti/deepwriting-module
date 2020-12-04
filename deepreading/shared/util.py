import numpy as np
import heapq
from sklearn.preprocessing import LabelEncoder


class HeapHelper(object):
    """
        Helper Class for heapq
    """
    def __init__(self, indices=[], value=0):
        self.indices = indices
        self.value = value

    def __lt__(self, other):
        return self.value < self.value


def parse_json(input_json):
    strokes = input_json['word_stroke']
    try:
        num_interpretations = input_json['num_interpretations']
    except KeyError:
        num_interpretations = 1

    # read strokes
    model_input = []
    for stroke in strokes:
        elem = [stroke['x'], stroke['y'], stroke['ev']]
        model_input.append(elem)

    model_input = np.array(model_input)
    # model_input = scale_to_zero_one(model_input)
    # model_input = translate_to_origin(model_input)
    model_input = calculate_diff(model_input)
    model_input = standartize_vector(model_input)

    # Add new dimension for batch_size
    model_input = np.expand_dims(model_input, axis=0)
    return model_input, num_interpretations


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


def process_result(result, alphabet, num_interpretations):
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

    # find probabilities of possible chars
    chars_collapsed = []
    history = []
    chars_probabilities = []
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

                # most_common = max(set(history), key=history.count)
                most_common = max(probability_dict, key=probability_dict.get)
                chars_probabilities.append(probability_dict)
                chars_collapsed.append(most_common)
            history = []

        if 'eow' in char:
            chars_collapsed.append(" ")
            chars_probabilities.append({" ": 1.0})

    # normalize probability dicts
    for d in chars_probabilities:
        prob_sum = sum([d[key] for key in d.keys()])
        for key in d.keys():
            d[key] = d[key] / prob_sum

    # convert dict into a list (per chacterposition) of list (possible chacter choices) of tuples
    chars_probabilities = [[(key, d[key]) for key in d]for d in chars_probabilities]

    # Sort list of possible character choices descendently
    [l.sort(key=lambda x: x[1], reverse=True) for l in chars_probabilities]

    # Find k most probable interpretations
    heap_list = []
    used_indices = []
    k_largest_sum = []

    # use min heap to get the k largest sums
    heap_helper = HeapHelper([0 for _ in chars_probabilities])
    heap_helper.value = -sum(chars_probabilities[i1][i2][1] for i1, i2 in enumerate(heap_helper.indices))
    heapq.heappush(heap_list, heap_helper)
    for i in range(num_interpretations):
        elem = heapq.heappop(heap_list)
        k_largest_sum.append(elem)

        for n in range(len(chars_probabilities)):
            indices = elem.indices.copy()
            # if there are no more elements don't increase by one
            if indices[n] >= len(chars_probabilities[n]) - 1:
                continue
            else:
                indices[n] += 1

            # check if the index combination is already in the heap
            h = hash(str(indices))
            if h not in used_indices:
                value = -sum([chars_probabilities[char_pos][char_index][1] for char_pos, char_index in enumerate(indices)])
                new_elem = HeapHelper(indices, value)
                heapq.heappush(heap_list, new_elem)
                used_indices.append(h)

    result_dict = {}
    for elem in k_largest_sum:
        result = ""
        prob = -(elem.value / len(chars_probabilities))
        for i1, i2 in enumerate(elem.indices):
            result += chars_probabilities[i1][i2][0]
        result_dict[str.rstrip(result)] = prob

    return result_dict
