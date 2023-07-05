# This script is used to install the required packages and run the application
python3 -m venv venv
source venv/bin/activate
pip install maturin
pip install pygame
maturin develop