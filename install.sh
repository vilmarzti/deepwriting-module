sudo apt update
sudo apt install build-essentials python3-dev libfreetype6-dev curl -y
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
poetry shell
pip install cython
poetry install