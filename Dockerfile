FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY scripts ./scripts

RUN mkdir -p faiss_index

EXPOSE 8000

CMD python scripts/build_vector_store.py && uvicorn app.main:app --host 0.0.0.0 --port 8000
