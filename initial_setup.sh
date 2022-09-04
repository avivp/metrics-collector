#!/bin/sh

pip install -r src/producer/requirements.txt
pip install -r src/consumer/requirements.txt
python $(pwd)/deployment/env_setup.py
