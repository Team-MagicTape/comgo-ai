#!/bin/bash

source venv/bin/activate

# uvicorn 실행 경로를 app/main.py로 변경합니다.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload