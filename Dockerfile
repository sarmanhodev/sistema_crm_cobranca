FROM python:3.11.5-slim

WORKDIR /crm_cobranca

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://0.0.0.0:8000/ || exit 1

CMD ["python", "main.py"]