FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
# CPU-only torch keeps the image small
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt
COPY common.py step*.py ./
ENV HF_HOME=/models
