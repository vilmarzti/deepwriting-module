import numpy as np


def parse_json(input_json):
    strokes = input_json['word_stroke']

    # read strokes
    model_input = []
    for stroke in strokes:
        elem = [stroke['x'], stroke['y'], stroke['ev']]
        model_input.append(elem)
    model_input = np.array(model_input)

    # Normalize the strokes
    # x_normalized = (model_input[:, 0] - np.mean(model_input[:, 0])) / np.linalg.norm(model_input[:, 0])
    # y_normalized = (model_input[:, 1] - np.mean(model_input[:, 0])) / np.linalg.norm(model_input[:, 1])
    # model_input = np.array([x_normalized, y_normalized, model_input[:, 2]]).transpose()

    # model_input = np.array([model_input[:, 0].astype('float'), model_input[:, 1].astype('float'), model_input[:, 2]]).transpose()

    x_transformed = model_input[:, 0]
    y_transformed = model_input[:, 1]
    
    # x_transformed = scale_to_zero_one(model_input[:, 0])
    # y_transformed = scale_to_zero_one(model_input[:, 1])

    # x_transformed = tranlsate_to_zero(x_transformed)
    # y_transformed = tranlsate_to_zero(y_transformed)

    x_transformed = calculate_diff(x_transformed)
    y_transformed = calculate_diff(y_transformed)

    x_transformed = standartize_vector(x_transformed)
    y_transformed = standartize_vector(y_transformed)

    model_input = np.array([x_transformed, y_transformed, model_input[1:, 2]]).transpose()

    # Add other dimension for model to predict
    model_input = np.expand_dims(model_input, axis=0)
    return model_input


def calculate_diff(vector):
    vector = np.array(vector).astype('float')
    vector = np.diff(vector)
    return vector


def tranlsate_to_zero(vector):
    origin = vector[0]
    return np.array([x - origin for x in vector])


def scale_to_zero_one(vector):
    minimum = np.min(vector)
    maximum = np.max(vector)
    vector = (vector - minimum) / (maximum - minimum)
    return vector 


def normalize_vector(vector):
    mean = np.mean(vector)
    return vector - mean


def standartize_vector(vector):
    mean = np.mean(vector)
    std = np.std(vector)
    vector = (vector - mean) / std
    return vector