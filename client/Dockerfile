FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fedcure_client.py .

# Hospital data is mounted at runtime via Docker volume:
#   -v ./data/hospital_1.csv:/data/hospital.csv
RUN mkdir -p /data

CMD ["python", "fedcure_client.py"]
