from flask import Flask, request
from flask_cors import CORS

from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

from ..shared import shared 
import numpy as np

app = Flask(__name__)
cors = CORS(app)

alphabet = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.,;:!?-+*()[]&/ \"#") # %:;&#
alphabet.insert(0, chr(0)) # '\x00' character, i.e., ord(0) to label concatenate
alphabet.insert(1, '\t') # start of sequence
alphabet.insert(2, '\n') # end of sequence

@app.route('/', methods=['POST'])
def evaluate():
    input_json = request.json
    model = load_model('./keras/seq2seq/model/best_model_seq_2_seq_256.hdf5')
    model_input = shared.parse_json(input_json)
    return result

if __name__ == '__main__':
    app.run(port=5000)