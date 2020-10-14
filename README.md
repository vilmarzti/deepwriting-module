# Deepwriting Module
In this project I try to recreate and improve the results from the [Deepwriting](https://ait.ethz.ch/projects/2018/deepwriting/) project. 

## Dependecies
### Poetry
I use poetry to take care of my project and install the needed dependencies. Check out [this](https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769) for further information on how to setup a project with poetry

### Node & typescript
The folder svg_utils uses typescript to compile flatten.ts to flatten.js in the `svg_utils/build/` folder.
Install node via `sudo apt install node`
Install typescript vis `sudo npm install -g typescript`

We also need to import certain libraries specified by `package.json`. Simply run `npm install` in `svg_utils` to install them

## Folder Structure
### Data
This folder contains various data. From SVG's we want to feed into the deeplearning frameworks to saved tensorflow models

### deepwriting
A fork of the deepwriting-project of the ETHZ. It contains all the files needed to setup the deepwriting-project

### keras
These are my attempts to build the language intrepreter of deepwriting. Using the same training and validation data
The different models use a server at port 5000 and expect a json file in the correct data-format.

To start a server use
`poetry run server-simple`
`poetry run server-seq2seq`

#### Baseline
This model tries to classify every stroke to a letter. The classified strokes are then merged into a simple letter based on the bow (beginning of word) and eoc (end of character) labels. These labels are also made by the simple model

#### Seq2Seq
This models uses a Sequence-to-Sequence model to interpret different strokes. This model has a bias towards creating a set of words if fed with single charcters.

### svg_util
These are some helper files that dissect the SVG files into the correct data-format for feeding them into various deepwriting setups.

This needs a deepwriting server running. See (keras)[#keras] on how to start a server

### touch_writing
The Website on which we can try out writing on a website and see the result from the deepwriting. This needs a running deepwriting server.
See on (keras)[#keras] how to start a server


## Errors
### Poetry could not install tensorflow 2.1.0
Run this command and everything should be set `poetry run pip install -U pip`

### Poetry could not install scikit-learn
There is a hidden dependency to cython. Open a shell with `poetry shell` and run `pip install cython`