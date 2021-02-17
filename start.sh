#!/usr/bin/env sh
set -e

celery -A engine.main worker -l INFO &\
python main.py discord
