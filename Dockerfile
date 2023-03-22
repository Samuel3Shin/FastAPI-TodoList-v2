FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip uninstall -y jose
RUN pip install python-jose==3.3.0

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]